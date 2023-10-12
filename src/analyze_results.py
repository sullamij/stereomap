import os
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go 
from src.utils import improve_text_position
import numpy as np 
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt 
from matplotlib import rc
from scipy import interpolate 
from scipy.spatial import ConvexHull
from adjustText import adjust_text 
import ast 
import scipy.stats as stats 
import numpy as np 

MODEL_NAME={'gpt-3.5-turbo':'GPT3.5','text-davinci-003':'Davinci','bard':'Bard'}
VALENCE=['Positive valence','Negative valence','Neutral valence']
DIMENSIONS=['Sociability','Morality','Ability','Agency','health','Status','work','Politics','Religion','beliefs_other','inhabitant',
'country','feelings','relatives','clothing','ordinariness','body_part','body_property',
'skin','body_covering','beauty','insults','stem','humanities','art','social_groups',
'Lacks_knowledge','fortune']


def retrieve_results(model='gpt-3.5-turbo',filetype='openended'):
    filelists=sorted(os.listdir('result/'))
    #filelists=sorted(os.listdir('result/v1'))
    file_filter=f'processed_{model}_{filetype}'
    #file_filter=f'processed_{model}'
    files_to_concat=[file for file in filelists if file_filter in file]
    #print(files_to_concat)
    for i, file in enumerate(files_to_concat):
        if i==0:
            df=pd.read_csv(f"result/{file}",index_col=[0])
            continue
        else:
            df_concat=pd.read_csv(f"result/{file}",index_col=[0])
            df=pd.concat([df,df_concat],ignore_index=True)
            
    return df

def count_nans(model='text-davinci-003'):
    cols={'openended':'Overall_Rating','emotion':'Contempt','behavior':'Help','socialconstruct':'Ratings'}
    results = retrieve_results(model)
    
    for i, col in enumerate(list(cols.keys())):
        if i==0:
            results=retrieve_results('Bard',col)
            results_nan=results[cols[col]].isnull().groupby([results['Group']]).value_counts(normalize=True).reset_index(name=f'Avg_{col}')
            results_nan=results_nan[results_nan[cols[col]]==True]
        else:
            results_=retrieve_results('Bard',col)
            results_nan_=results_[cols[col]].isnull().groupby([results_['Group']]).value_counts(normalize=True).reset_index(name=f'Avg_{col}')
            results_nan_=results_nan_[results_nan_[cols[col]]==True]

            results_nan=pd.merge(results_nan,results_nan_,on='Group',how='outer')

    for col in [t for t in list(results_nan.columns)if 'Avg' in t]:
        results_nan[col]=results_nan[col].apply(lambda x: 0 if pd.isna(x) else x)
    
    results_nan['Avg_nans']=results_nan.apply(lambda x: np.average([x[col] for col in list(results_nan.columns) if ('Avg' in col) and  (not pd.isna(x[col]))]) ,axis=1)
    results_nan.sort_values(['Avg_nans'],ascending=False)
    return results_nan.sort_values(['Avg_nans'],ascending=False)
    

def count_ratings(df):
    df['Ratings']=df['Ratings'].apply(lambda x:str(x))
    filtered=df.query("Ratings!='nan'")
    filtered['Ratings'] = filtered['Ratings'].apply(lambda x:float(x))
    ratings=filtered.groupby(['Group']).apply(lambda grp:grp.groupby('Construct')['Ratings'].mean().to_dict()).to_dict()
    return ratings

def plot_scatter(df,model='gpt-3.5-turbo'):
    #df=retrieve_results(model)
    ratings = count_ratings(df)
    RATING=pd.DataFrame.from_dict(ratings,orient='index').rename_axis('Group').reset_index()
    RATING['Competence'] =RATING['Competence'].apply(lambda x:float(x))
    RATING['Warmth'] = RATING['Warmth'].apply(lambda x:float(x))
    RATING=RATING.sort_values(['Competence','Warmth'])

    plot = px.scatter(RATING,x='Competence',y='Warmth',text='Group',size_max=60,opacity=0.9)
    #plot.update_traces(textposition=improve_text_position(RATING['Competence']))
    plot.update_layout(height=1000,
                       title={
                           'text':MODEL_NAME[model],
                           #'y':0.9,
                           'x':0.5,
                           'xanchor':'center',
                           'yanchor':'top'
                       })#template='plotly_white')
    plot.update_xaxes(title_text='Competence',title_font= {'family':'Times New Roman', 'size': 23})
    plot.update_yaxes(title_text='Warmth',  title_font = {'family':'Times New Roman', 'size': 23})
    plot.update_layout(font=dict(
                family='Times New Roman', 
                size=19, 
            ))
    
    return plot, RATING

def calc_warmth_competence(df=None,model=None,filetype='openended'):
    if model:
        df=retrieve_results(model=model)
    df['Sociability']=(df['Friendly']+df['Sociable'])/2
    df['Morality']=(df['Trustworthy']+df['Honest'])/2
    df['Ability']=(df['Competent']+df['Skilled'])/2
    df['Assertiveness']=(df['Confident']+df['Assertive'])/2
    df['Warmth']=(df['Sociability']+df['Morality'])/2
    df['Competence']=(df['Ability']+df['Assertiveness'])/2

    df=df.dropna(subset=['Warmth','Competence'])
    ratings=df.groupby(['Group'])[['Warmth','Competence']].aggregate('mean').to_dict()
    df=pd.DataFrame.from_dict(ratings).rename_axis('Group').reset_index()
    df['Competence']=df['Competence'].apply(lambda x:float(x))
    df['Warmth']=df['Warmth'].apply(lambda x:float(x))
    df['Group']=df['Group'].apply(lambda x: x.capitalize())
    df=df.sort_values(['Competence','Warmth'])
    return df

def calc_kmeans(df,model_name):
    kmeans = KMeans(n_clusters=5, random_state=0)
    df['Cluster'] = kmeans.fit_predict(df[['Warmth','Competence']])

    # get centroids 
    centroids = kmeans.cluster_centers_
    cen_x = [i[0] for i in centroids]
    cen_y = [i[1] for i in centroids]

    #add df 
    df['cen_x'] = df.Cluster.map({0:cen_x[0],1:cen_x[1],2:cen_x[2],3:cen_x[3],4:cen_x[4]})
    df['cen_y'] = df.Cluster.map({0:cen_y[0],1:cen_y[1],2:cen_y[2],3:cen_y[3],4:cen_x[4]})

    # define map colors 
    COLOR={'purple':'#6929c4','cyan':'#1192e8','teal':'#005d5d','magenta':'#9f1853','orange':'#8a3800'}
    if model_name=='all':
        colors=[COLOR['magenta'],COLOR['teal'],COLOR['purple'],COLOR['orange'],COLOR['cyan']]  # all
    elif model_name=='davinci':
        colors=[COLOR['orange'],COLOR['cyan'],COLOR['purple'],COLOR['magenta'],COLOR['teal']] # davinci
    elif model_name=='gpt35':
        colors=[COLOR['purple'],COLOR['magenta'],COLOR['cyan'],COLOR['orange'],COLOR['teal']] # gpt35
    elif model_name=='bard':
        colors=[COLOR['magenta'],COLOR['purple'],COLOR['orange'],COLOR['cyan'],COLOR['teal']] # bard
    #colors=[COLOR['magenta'],COLOR['teal'],COLOR['purple'],COLOR['orange'],COLOR['cyan']] # all

    #colors = ['#6929c4','#1192e8','#005d5d','#9f1853']
    df['c'] = df.Cluster.map({0:colors[0],1:colors[1],2:colors[2],3:colors[3],4:colors[4]})
    return df

def plot_warmth_competence(df,model_name=None):
    fig,ax=plt.subplots(1,figsize=(12,10))
    plt.scatter(df.Competence, df.Warmth,c=df.c,alpha=0.6,s=10)
    colors = ['#6929c4','#1192e8','#005d5d','#9f1853']
    COLOR={'purple':'#6929c4','cyan':'#1192e8','teal':'#005d5d','magenta':'#9f1853','orange':'#8a3800'}

    if model_name=='All':
        colors=[COLOR['magenta'],COLOR['teal'],COLOR['purple'],COLOR['orange'],COLOR['cyan']]  # all
    elif model_name=='DAVINCI':
        colors=[COLOR['orange'],COLOR['cyan'],COLOR['purple'],COLOR['magenta'],COLOR['teal']] # davinci
    elif model_name=='GPT-3.5':
        colors=[COLOR['purple'],COLOR['magenta'],COLOR['cyan'],COLOR['orange'],COLOR['teal']] # gpt35
    elif model_name=='BARD':
        colors=[COLOR['magenta'],COLOR['purple'],COLOR['orange'],COLOR['cyan'],COLOR['teal']] # bard
    #colors=[COLOR['magenta'],COLOR['teal'],COLOR['purple'],COLOR['orange'],COLOR['cyan']] # all


    #plt.scatter(cen_x,cen_y,c=colors)
    #for i, row in df.iterrows():
    #    ax.annotate(row['Group'],(row['Competence'],row['Warmth']))
    texts = [plt.text(row['Competence'],row['Warmth'], row['Group'], ha='center', va='center') for i, row in df.iterrows()]
    #adjust_text(texts, arrowprops=dict(arrowstyle='->',color='black'))
    adjust_text(texts)
    rc('font',**{'family':'Times new roman','serif':['Times']})
    plt.xlabel('Competence')
    plt.ylabel('Warmth')
    if model_name:
        plt.title(model_name,fontsize=22)
    plt.rc('axes',labelsize=18)

    for i in df.Cluster.unique():
        # get the convex hull 
        points = df[df.Cluster==i][['Competence','Warmth']].values 
        hull=ConvexHull(points)
        x_hull = np.append(points[hull.vertices,0],points[hull.vertices,0][0])
        y_hull = np.append(points[hull.vertices,1],points[hull.vertices,1][0])
        #interpolate 
        dist = np.sqrt((x_hull[:-1] - x_hull[1:])**2 + (y_hull[:-1] - y_hull[1:])**2)
        dist_along = np.concatenate(([0], dist.cumsum()))
        spline, u = interpolate.splprep([x_hull, y_hull], 
                                        u=dist_along, s=0, per=1)
        interp_d = np.linspace(dist_along[0], dist_along[-1], 50)
        interp_x, interp_y = interpolate.splev(interp_d, spline)
        # plot shape
        plt.fill(interp_x, interp_y, '--', c=colors[i], alpha=0.1)
    
    return fig 

def count_overall_rating(df=None,model='text-davinci-003',filetype='openended'):
    def preprocess(df):
        df['Overall_Rating']=df['Overall_Rating'].apply(lambda x: ast.literal_eval(x)[0]) 
        for i, row in df.iterrows():
            if not row['Overall_Rating']:
                df=df.drop(i)
                continue
            if row['Overall_Rating']=='NaN' or row['Overall_Rating']==[]:
                df=df.drop(i)
                continue
        return df
        
    if model!='All':
        davinci=retrieve_results(model='text-davinci-003',filetype=filetype)
        davinci=preprocess(davinci)
        gpt35=retrieve_results(model='gpt-3.5-turbo',filetype=filetype)
        gpt35=preprocess(gpt35)
        bard=retrieve_results(model='Bard',filetype=filetype)
        df = pd.concat([davinci,gpt35,bard])
    if model and model!='All':
        df=retrieve_results(model=model,filetype=filetype)
        if model !='Bard':
            df = preprocess(df)
        df=df.dropna(subset=['Overall_Rating'])
    df['Overall_Rating']=df['Overall_Rating'].apply(lambda x: float(x))
    dimensions=['Overall_Rating']
    df=df.groupby(['Group'])[dimensions].aggregate(['mean','var']).reset_index()
    return df

def search_dictionary(keyword,dictionary=None):
    if not dictionary:
        dictionary_dir='data/Full Dictionaries.csv'
        dictionary=pd.read_csv(dictionary_dir)
    extracted={}
    filtered=dictionary.query("`original word`==@keyword")
    if len(filtered)==0:
        print(f'{keyword} doesnt exist!')
        return {}
    else:
        for valence in VALENCE:
            extracted[valence]=filtered[valence].values[0]
        for dimension in DIMENSIONS:
            if filtered[f'{dimension} dictionary'].values[0]==1:
                if f"{dimension} direction" in filtered.columns:
                    extracted[dimension]=filtered[f'{dimension} direction'].values[0]
                else:
                    extracted[dimension]=filtered[f'{dimension} dictionary'].values[0]

    return extracted

def get_cluster_df(df=None,model='text-davinci-003'):
    MODEL_NAME={'text-davinci-003':'DAVINCI','gpt-3.5-turbo':'GPT-3.5','Bard':'BARD','All':'All'}
    MODEL_NAME2={'text-davinci-003':'davinci','gpt-3.5-turbo':'gpt35','Bard':'bard','All':'All'}
    if model and model!='All':
        df = retrieve_results(model=model)
    df = calc_warmth_competence(df)
    df = calc_kmeans(df,MODEL_NAME2[model])
    CLUSTER_MAP={df[df['Group']=='Homeless']['Cluster'].values[0]:0,df[df['Group']=='Lower-class']['Cluster'].values[0]:1,df[df['Group']=='Lawyers']['Cluster'].values[0]:2,
             df[df['Group']=='Elderly']['Cluster'].values[0]:3,df[df['Group']=='Nurses']['Cluster'].values[0]:4}
    df['NCluster']=df.Cluster.map(CLUSTER_MAP)
    return df

def compute_corr(df, model_name):
    df=df.dropna()
    variables1 = ['Competence','Warmth']
    variables2 = ['Competition-others','Status']
    print(f" Correlation {model_name}")
    for i, var in enumerate(variables1):
        for j, var1 in enumerate(variables2): 
            corr, p =stats.spearmanr(df[var], df[var1])
            print(f"Correlation of {var} and {var1}: {np.round(corr,2)}, {np.round(p,2)}")