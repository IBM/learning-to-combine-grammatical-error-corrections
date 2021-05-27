import numpy as np
import argparse
import pandas as pd

from scipy.optimize import minimize

# Calculates for f-beta measure
def fbeta(tp, fp, fn, beta):
    return (1.0 + beta * beta) * tp / ((1.0 + beta * beta) * tp + beta * beta * fn + fp)


# Global variables used in the the target(x) method
fp_array = None
tp_array = None
total_p = 0
beta = 0.5

# Minumum predictions required for selecting a category
min_predictions = 2

def calculate_minus_fbeta_on_selection(x):
    tp = np.inner(tp_array, x)
    fp = np.inner(fp_array, x)
    fn = total_p - tp
    return -fbeta(tp, fp, fn, beta)


def load_m2_result_file(file):
    result = np.genfromtxt(file, dtype=[('cat','U13'),('tp','i8'),('fp','i8'),('fn','i8')], delimiter="", skip_header=3, skip_footer=4, usecols=[0, 1, 2, 3])
    cat_array = result['cat']
    tp_array = result['tp']
    fp_array = result['fp']
    fn_array = result['fn']
    return cat_array,tp_array, fp_array, fn_array

def save_model(file,cat_array,sel_array):
    assert len(cat_array) == len(sel_array)
    model = np.empty((len(cat_array),),dtype=[('cat','U13'),('sel','f8')])
    model['cat'] = cat_array
    model['sel'] = sel_array
    print("Saving " + file)
    print([ cat for i,cat in enumerate(cat_array) if sel_array[i] > 0])
    np.savetxt(file,model,fmt="%s")


def print_debug(df):
    df = df.assign(total=df.tp_AminusB + df.fn_AminusB)
    df = df.assign(p_AminusB=df.tp_AminusB / (df.tp_AminusB + df.fp_AminusB))
    df = df.assign(r_AminusB=df.tp_AminusB / df.total)

    df = df.assign(p_AandB=df.tp_AandB / (df.tp_AandB + df.fp_AandB))
    df = df.assign(r_AandB=df.tp_AandB / df.total)

    df = df.assign(p_BminusA=df.tp_BminusA / (df.tp_BminusA + df.fp_BminusA))
    df = df.assign(r_BminusA=df.tp_BminusA / df.total)
    df = df.assign(percent = df.total / sum(df.total))
    df = df.sort_values(by='total')
    df = df.round(2)
    df = df[ [ 'category', 'percent' , 'sel_AminusB' ,'p_AminusB', 'r_AminusB','sel_AandB', 'p_AandB' , 'r_AandB', 'sel_BminusA' , 'p_BminusA', 'r_BminusA']]
    df = df.tail(10)
    #df.to_csv('debug.csv',sep='&',index=False)
    print(df.to_string())


def main(args):
    global tp_array
    global fp_array
    global total_p

    print("Merging " + args.trainAminusB + " and " + args.trainBminusA + " and " + args.trainAandB + "...")
    cat_AminusB,tp_AminusB, fp_AminusB, fn_AminusB = load_m2_result_file(args.trainAminusB)
    cat_BminusA,tp_BminusA, fp_BminusA, fn_BminusA = load_m2_result_file(args.trainBminusA)
    cat_AandB,tp_AandB, fp_AandB, fn_AandB = load_m2_result_file(args.trainAandB)

    assert tp_AminusB.shape == tp_BminusA.shape
    assert tp_AminusB.shape == tp_AandB.shape

    total_p = np.sum(tp_AminusB) + np.sum(fn_AminusB)
    assert total_p == np.sum(tp_BminusA) + np.sum(fn_BminusA)
    assert total_p == np.sum(tp_AandB) + np.sum(fn_AandB)

    tp_array = np.concatenate([tp_AminusB, tp_BminusA, tp_AandB])
    fp_array = np.concatenate([fp_AminusB, fp_BminusA, fp_AandB])

    print("Baseline Fbeta when we take all corrections from all files:")
    s = np.ones(tp_array.shape[0])
    print(-calculate_minus_fbeta_on_selection(s))


    print("Find optimial subset of correction that maximize f-beta:")
    bounds = [(0, 1) for i in range(0, s.shape[0])]
    res = minimize(calculate_minus_fbeta_on_selection, s, bounds=bounds)
    print(res.message)
    print(-calculate_minus_fbeta_on_selection(res.x))

    print("Limit to only categories with atleast " + str(min_predictions))
    pred_array = np.add(tp_array,fp_array)
    limited_pred_array = res.x * (pred_array >= min_predictions)
    print(limited_pred_array)
    print(-calculate_minus_fbeta_on_selection(limited_pred_array))

    print("Round selection to 0 or 1")
    rounded_pred_array = np.round(limited_pred_array)
    print(rounded_pred_array)
    print(-calculate_minus_fbeta_on_selection(rounded_pred_array))

    sel_AminusB,sel_BminusA,sel_AandB = np.split(rounded_pred_array,3)

    df = pd.DataFrame({ 'category' : cat_AminusB,
                        'sel_AminusB' : sel_AminusB,
                        'tp_AminusB' : tp_AminusB,
                        'fp_AminusB' : fp_AminusB,
                        'fn_AminusB': fn_AminusB,
                        'sel_AandB': sel_AandB,
                        'tp_AandB': tp_AandB,
                        'fp_AandB': fp_AandB,
                        'fn_AandB': fn_AandB,
                        'sel_BminusA': sel_BminusA,
                        'tp_BminusA': tp_BminusA,
                        'fp_BminusA': fp_BminusA,
                        'fn_BminusA': fn_BminusA})
    print_debug(df);

    save_model(args.modelAminusB, cat_AminusB,sel_AminusB)
    save_model(args.modelBminusA, cat_BminusA,sel_BminusA)
    save_model(args.modelAandB, cat_AandB,sel_AandB)

if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description="Program to find subset of m2 corrections that optimized f-beta over disjoint files",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="%(prog)s -files FILES [FILES ...]")
    parser.add_argument("-trainAminusB", help="The path of first m2 file filtered by the second m2 used in training",
                        required=True)
    parser.add_argument("-trainBminusA", help="The path of second m2 file filtered by the first m1 using in training",
                        required=True)
    parser.add_argument("-trainAandB", help="The path of common annotations m2 file used in training", required=True)
    parser.add_argument("-modelAminusB", help="The path of model for first m2 filtered by the second m2",
                        required=True)
    parser.add_argument("-modelBminusA", help="The path of nmdel for second m2 filtered by the first m2",
                        required=True)
    parser.add_argument("-modelAandB", help="The path of model of the common m2 file  ", required=True)

    args = parser.parse_args()
    main(args)
