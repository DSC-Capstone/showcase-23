import pandas as pd
import numpy as np
import yaml, json
import os
import re

# from IPython.display import display, HTML

template_path = 'index-template.html'
sheet_path = 'Public-Facing Block Assignments – DSC 180AB, 2022-23 - Sheet1.csv'
ASGN_NAME = 'assignment_2739086_export'

toc_map = {}

format_anchor = lambda s: '-'.join(s[:-1].strip().lower().split())

with open(template_path, 'r') as f:
    template = f.read()
    
df = pd.read_csv(sheet_path)
df = df.iloc[1:].reset_index(drop=True)
df['Section'] = df['Group #'].str.split('-').str[0]

mentors = pd.read_csv('2022-23 Student-Facing Capstone Scheduling Sheet - Sheet3.csv', 
                      header=None)
mentors.columns = ['Section', 'Mentors']
posters = pd.read_csv('Poster links - Sheet1.csv')
reports = pd.read_csv('Report links - Sheet1.csv')
reports['Group #'] = reports['File'].str.replace('.pdf', '')
posters['Group #'] = posters['File'].str.extract(r'([AB]\d{2,3}-\d)')

df = df.merge(mentors, on='Section', how='left').merge(posters, on='Group #', how='left').merge(reports, on='Group #', how='left').fillna('#')

# Now, add abstract/website link/code link/paper link

def load_artifacts(sub):
    artifacts = json.load(open(f'{ASGN_NAME}/{sub}/artifacts.json', 'r'))
    code = artifacts['project-repository']
    if code[-4:] == '.git':
        code = code[:-4]
    website = artifacts['project-website-url']
    return code, website

def load_title_abstract(sub):
    f = open(f'{ASGN_NAME}/{sub}/title-abstract.txt', 'r').read()
    try:
        title = re.findall(r'Title:\n?(.+)', f)[0]
    except:
        return(sub)
    title = title.strip().replace('<', '').replace('>', '')
    abstract = re.findall(r'Abstract:\n?(.+)', f)[0]
    return title, abstract

# def copy_poster(sub, group):
#     os.system(f'cp {ASGN_NAME}/{sub}/report.pdf ../reports/{group}.pdf')

meta = yaml.safe_load(
    open(f'{ASGN_NAME}/submission_metadata.yml', 'r')
    )

def process_metadata(meta):
    out_df = pd.DataFrame(columns=['Group #', 'Code', 'Website', 'Title', 'Abstract'])

    for sub in meta:
        try:
            name = meta[sub][':submitters'][0][':name']
        except Exception as e:
            pass
            print(sub)
        if name == 'Alison Dunning':
            name = 'Camille Dunning'
        row = df[df['Names'].str.contains(name)]
        if len(row) != 1:
            pass
            print(row)
        else:
            row = row.iloc[0]
            group = row['Group #']
            try:
                code, website = load_artifacts(sub)
                title, abstract = load_title_abstract(sub)
                # copy_poster(sub, group)
                s_dict = {'Group #': group, 
                        'Code': code, 
                        'Website': website, 
                        'Title': title,
                        'Abstract': abstract}
                out_df = pd.concat([out_df, pd.DataFrame([s_dict])])
            except Exception as e:
                print(e)
    
    out_df = out_df.groupby('Group #').last().reset_index()
    return out_df

df = df.merge(process_metadata(meta), on='Group #', how='left').fillna('#')

# Manual fixes for typos

df.loc[df['Group #'] == 'B08-1', 'Code'] = 'https://github.com/ESR76/Capstone-Brick-Modeling'
df.loc[df['Group #'] == 'B319-3', 'Code'] = 'https://github.com/TallMessiWu/dota2-drafting-backend'
df.loc[df['Group #'] == 'A11-2', 'Code'] = 'https://github.com/bliu8923/dsc180b-project'

print(df.loc[df['Group #'] == 'A11-1'].iloc[0])

def format_project(row):
    mentor_label = 'Mentors' if ('and' in row['Mentors'] or ',' in row['Mentors']) else 'Mentor'
    return f'''
<b>{row["Project Title"]}</b>
<p>Group {row["Group #"]}: {row["Names"]} ({mentor_label}: {row['Mentors']})<br>
<a href="{row['URL']}">🪧 Poster</a> • <a href="{row['Website']}">🌐 Website</a> • <a href="{row["Report URL"]}.pdf">📖 Report</a> • <a href="{row['Code']}">💻 Code</a><br></p>
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
    out = ''
    for block in np.sort(df['Block (see hdsishowcase.com)'].unique()):
        out += process_block(block)
    out = format_toc(toc_map) + '\n<br>\n' + out
    out = template.replace('### REPLACE ###', out)
    with open('../index.html', 'w') as f:
        f.write(out)
        
write_all()