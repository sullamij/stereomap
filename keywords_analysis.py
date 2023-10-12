import pandas as pd 
import os 
from src.analyze_results import * 
from collections import Counter, defaultdict
from itertools import permutations 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


df_cluster = get_cluster_df(model='Bard')
df = retrieve_results('Bard','openended')

Words={}
lemmatizer = WordNetLemmatizer()
for group in list(df.Group.unique()): 
    Words[group]=Counter()

for i, row in df.iterrows():
    group=row['Group']
    keywords=ast.literal_eval(row['Keywords'])
    if keywords==['NaN']:
        continue 
    keywords=[k.strip().lower() for k in keywords]
    keywords=[lemmatizer.lemmatize(k) for k in keywords]
    #keywords=[re.sub(r'[^\w\s]','',k) for k in keywords]

    keywords=[k for k in keywords if not len(k.split(" "))>1]
    Words[group].update(keywords)

total_words = []
for group in Words.keys():
    for dic in Words[group].items():
        total_words.append(dic[0])

group_cluster={}
for i, row in df_cluster.iterrows():
    group_cluster[row['Group'].lower()]=row['NCluster']

for group in Words.keys():
    total=sum(Words[group].values(),0.0)
    for key in Words[group]:
        Words[group][key] /=total

cluster_counter = {}
for cluster in list(df_cluster.NCluster.unique()):
    cluster_counter[cluster]=Counter()

for word in Words.keys():
    if word.lower() not in group_cluster.keys():
        continue
    cluster_counter[group_cluster[word.lower()]].update(Words[word])

Cluster_set={}
for cluster in list(cluster_counter.keys()):
    Cluster_set[cluster] = set(cluster_counter[cluster].keys())


perm = list(permutations([0,1,2,3]))
perm=[perm[0],perm[6],perm[12],perm[18]]

for p in perm: #### text-davinci-003
    print(f"Unique {p[0]}: {len(Cluster_set[p[0]].difference(Cluster_set[p[1]]).difference(Cluster_set[p[2]]).difference(Cluster_set[p[3]]))}")
print(f"Intersection: {len(Cluster_set[p[0]].intersection(Cluster_set[p[1]]).intersection(Cluster_set[p[2]]).intersection(Cluster_set[p[3]]))}")

Cluster_Result={}
for cluster in cluster_counter.keys():
    Cluster_Result[cluster]=[]

for cluster in cluster_counter.keys():
    keywords=cluster_counter[cluster]
    for k in keywords:
        if search_dictionary(k):
            Cluster_Result[cluster].append({k:search_dictionary(k)})

DIMENSION_GROUP_CLUSTER = defaultdict(list)

# calculate valence 
for group in Cluster_Result.keys():
    keywords=Cluster_Result[group]
    for key in keywords: 
        dimensions=list(key.items())[0][1]
        for dim in dimensions.keys(): 
            if dim not in ['Positive valence','Negative valence', 'Neutral valence']:
                DIMENSION_GROUP_CLUSTER[group].append({dim:dimensions[dim]})

DIMENSION_GROUP_CLUSTER_CALC ={} 
for group in DIMENSION_GROUP_CLUSTER.keys():
    dic={}
    total_words = len(DIMENSION_GROUP_CLUSTER[group])
    keywords=set(list(item.keys())[0] for item in DIMENSION_GROUP_CLUSTER[group])
    for keyword in keywords:
        dic[keyword]=0 
    for att in DIMENSION_GROUP_CLUSTER[group]:
        k = list(att.keys())[0]
        dic[k]+=att[k]
    for key in dic.keys():
        dic[key]=dic[key]/total_words
    DIMENSION_GROUP_CLUSTER_CALC[group]=dic

df = pd.DataFrame()
for cluster in DIMENSION_GROUP_CLUSTER_CALC.keys():
    for k in DIMENSION_GROUP_CLUSTER_CALC[cluster].keys():
        dr=pd.DataFrame([{'Cluster':cluster,'Dimension':k,'Value':DIMENSION_GROUP_CLUSTER_CALC[cluster][k]}])
        df=pd.concat([df,dr],ignore_index=True)

df=df.reindex(df['Value'].abs().sort_values(ascending=False).index)

def hex_to_rgba(h, alpha):
    '''
    converts color value in hex format to rgba format with alpha transparency
    '''
    return tuple([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] + [alpha])


fig = make_subplots(rows=1,cols=5)
COLOR={'purple':'#6929c4','cyan':'#1192e8','teal':'#005d5d','magenta':'#9f1853','orange':'#8a3800'}
colors=[COLOR['teal'],COLOR['orange'],COLOR['purple'],COLOR['cyan'],COLOR['magenta']]

fig.append_trace(go.Bar(
    x=df[df['Cluster']==0]['Dimension'].head(5).tolist(),
    y=df[df['Cluster']==0]['Value'].head(5).tolist(),
    offsetgroup=0,
    text=df[df['Cluster']==0]['Dimension'],
    showlegend=False,
    marker={'color':'rgba'+str(hex_to_rgba(colors[0],0.3))},
marker_line=dict(color='rgba'+str(hex_to_rgba(colors[0],1)),width=1),
textfont=dict(color='Black')),row=1,col=1)

fig.append_trace(go.Bar(
    x=df[df['Cluster']==1]['Dimension'].head(5).tolist(),
    y=df[df['Cluster']==1]['Value'].head(5).tolist(),
    offsetgroup=0,
    text=df[df['Cluster']==1]['Dimension'],
    showlegend=False,
    marker={'color':'rgba'+str(hex_to_rgba(colors[1],0.3))},
marker_line=dict(color='rgba'+str(hex_to_rgba(colors[1],1)),width=1),
textfont=dict(color='Black')),row=1,col=2)

fig.append_trace(go.Bar(
    x=df[df['Cluster']==2]['Dimension'].head(5).tolist(),
    y=df[df['Cluster']==2]['Value'].head(5).tolist(),
    offsetgroup=0,
    text=df[df['Cluster']==2]['Dimension'],
    showlegend=False,
    marker={'color':'rgba'+str(hex_to_rgba(colors[2],0.3))},
marker_line=dict(color='rgba'+str(hex_to_rgba(colors[2],1)),width=1),
textfont=dict(color='Black')),row=1,col=3)

fig.append_trace(go.Bar(
    x=df[df['Cluster']==3]['Dimension'].head(5).tolist(),
    y=df[df['Cluster']==3]['Value'].head(5).tolist(),
    offsetgroup=0,
    text=df[df['Cluster']==3]['Dimension'],
    showlegend=False,
    marker={'color':'rgba'+str(hex_to_rgba(colors[3],0.3))},
marker_line=dict(color='rgba'+str(hex_to_rgba(colors[3],1)),width=1),
textfont=dict(color='Black')),row=1,col=4)

fig.append_trace(go.Bar(
    x=df[df['Cluster']==4]['Dimension'].head(5).tolist(),
    y=df[df['Cluster']==4]['Value'].head(5).tolist(),
    offsetgroup=0,
    text=df[df['Cluster']==4]['Dimension'],
    showlegend=False,
    marker={'color':'rgba'+str(hex_to_rgba(colors[4],0.3))},
marker_line=dict(color='rgba'+str(hex_to_rgba(colors[4],1)),width=1),
textfont=dict(color='Black')),row=1,col=5)

fig.update_xaxes(showticklabels=False)
fig['layout']['xaxis']['title']='Cluster 0'
fig['layout']['xaxis2']['title']='Cluster 1'
fig['layout']['xaxis3']['title']='Cluster 2'
fig['layout']['xaxis4']['title']='Cluster 3'
fig['layout']['xaxis5']['title']='Cluster 4'

fig.add_annotation(text='Direction',xref='paper',yref='paper',x=-0.05,y=0.4,textangle=-90,
                   font=dict(size=18) )
#fig.add_annotation(text='Dimensions',xref='paper',yref='paper',x=0.15,y=-0.1,
#                   font=dict(size=18),showarrow=False)
#fig.add_annotation(text='Dimensions',xref='paper',yref='paper',x=1-0.15,y=-0.1,
#                   font=dict(size=18),showarrow=False)

fig.update_layout(
    width=1200,
    template='plotly_white',
    font=dict(
    family='Times New Roman',
    size=20,
    color='Black',
))

fig.update_traces(textposition='inside')
fig.update_layout(uniformtext_minsize=22 )
fig.write_image('result/Figure/BARD-Cluster-Keywords.pdf')