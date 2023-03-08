import pandas as pd
import numpy as np

# from IPython.display import display, HTML

template_path = 'index-template.html'
sheet_path = 'Public-Facing Block Assignments – DSC 180AB, 2022-23 - Sheet1.csv'

toc_map = {}

format_anchor = lambda s: '-'.join(s[:-1].strip().lower().split())

with open(template_path, 'r') as f:
    template = f.read()
    
df = pd.read_csv(sheet_path)
df = df.iloc[1:].reset_index(drop=True)

def format_project(row):
    return f'''
<b>{row["Project Title"]}</b>
<p>Group {row["Group #"]}: {row["Names"]}</p>
    '''

def process_broad_area(area, block):
    toc_map[block][area] = format_anchor(area)
    out = f'<a name="{format_anchor(area)}"></a>\n<h4>{area}</h4>\n'
    area_df = df[df['Broad area'] == area].copy().sort_values('Group #')
    for i, r in area_df.iterrows():
        out += format_project(r) + '\n'
    return out + '\n<br>'

def process_block(block):
    toc_map[block] = {}
    out = f'<h3>Block {block}</h3>\n<br>\n'
    for area in np.sort(df.loc[df['Block (see hdsishowcase.com)'] == block, 'Broad area'].unique()):
        out += process_broad_area(area, block)
        
    return out + '\n<br>\n'

def format_toc(toc_map):
    out = '<h4>Table of Contents</h4>'
    for block in toc_map:
        out += f'<b>Block {block}</b>:'
        out += '\n<ul>'
        for area in toc_map[block]:
            out += f'<li><a href="#{toc_map[block][area]}">{area}</a></li>\n'
        out += '\n</ul>'
    out += '\n<br>'
    return out

def write_all():
    out = format_toc(toc_map)
    for block in np.sort(df['Block (see hdsishowcase.com)'].unique()):
        out += process_block(block)
    out = template.replace('### REPLACE ###', out)
    with open('../index.html', 'w') as f:
        f.write(out)
        
write_all()
