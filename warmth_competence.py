import os 
import pandas as pd 
from argparse import ArgumentParser
from scipy import stats 
from src.analyze_results import retrieve_results, calc_warmth_competence, calc_kmeans, plot_warmth_competence

MODEL_NAME = {'text-davinci-003':'DAVINCI','gpt-3.5-turbo':'GPT-3.5','Bard':'BARD'}

if __name__=='__main__':

    parser:ArgumentParser = ArgumentParser()
    parser.add_argument('--model',help='Select from: [Bard,text-davinci-003,gpt-3.5-turbo]')
    parser.add_argument('--save_dir',help='save directory')

    args=parser.parse_args() 

    df = retrieve_results(model=args.model)
    df = calc_warmth_competence(model = args.model)
    df = calc_kmeans(df)
    fig = plot_warmth_competence(df, model_name =MODEL_NAME[args.model])
    fig.savefig(args.save_dir, bbox_inches='tight',format='pdf')

    ### t-test 
    print(stats.ttest_rel(df[df['Cluster']==0]['Warmth'].tolist(),df[df['Cluster']==0]['Competence'])) # lower-class, black
    print(df[df['Cluster']==0][['cen_y','cen_x','Group']].head(1))

    print(stats.ttest_rel(df[df['Cluster']==1]['Warmth'].tolist(),df[df['Cluster']==1]['Competence']))  # elderly, children 
    print(df[df['Cluster']==1][['cen_y','cen_x','Group']].head(1))

    print(stats.ttest_rel(df[df['Cluster']==2]['Warmth'].tolist(),df[df['Cluster']==2]['Competence'])) # rich, CEOs
    print(df[df['Cluster']==2][['cen_y','cen_x','Group']].head(1))

    print(stats.ttest_rel(df[df['Cluster']==3]['Warmth'].tolist(),df[df['Cluster']==3]['Competence'])) #nurse doctors
    print(df[df['Cluster']==3][['cen_y','cen_x','Group']].head(1))


    print(stats.ttest_rel(df[df['Cluster']==4]['Warmth'].tolist(),df[df['Cluster']==4]['Competence'])) #poor, drug addict 
    print(df[df['Cluster']==4][['cen_y','cen_x','Group']].head(1))


    
