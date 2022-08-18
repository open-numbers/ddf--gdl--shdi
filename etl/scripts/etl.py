# %%
import pandas as pd
import numpy as np
import os

from ddf_utils.str import to_concept_id
# %%
# %%
# configuration of file path
desc_file = '../source/SHDI-SGDI-5.0-Vardescription.csv'
data_file = '../source/SHDI-SGDI-Total 5.0.csv'
out_dir = '../../'
# %%
# %%
data = pd.read_csv(data_file, encoding='iso-8859-1', skipinitialspace=True)
desc = pd.read_csv(desc_file, encoding='iso-8859-1')
# %%
data.head()
# %%
desc.head()
# %%
ents = data[['iso_code', 'country', 'GDLCODE', 'level', 'region']].copy()
# %%
ents = ents.drop_duplicates(subset=['GDLCODE'])
# %%
ents['level'].unique()
# %%
nat = ents[ents['level'] == 'National'].copy()
# %%
nat = nat.set_index('GDLCODE')
# %%
nat.columns = ['iso_code', 'name', 'level', 'region']
# %%
nat = nat.drop(columns=['level', 'region'])
nat['is--national'] = 'TRUE'
nat['national'] = nat.index.map(to_concept_id)
nat.index.name = 'gdlcode'
nat = nat.reset_index().set_index('national')
# %%
nat.to_csv('../../ddf--entities--level--national.csv')
# %%
natmap = nat['iso_code'].to_dict()
natmap = dict([(v, k) for k, v in natmap.items()])
# %%
# Subnat
subnat = ents[ents.level == 'Subnat']
# %%
subnat = subnat.set_index('GDLCODE')
subnat.index.name = 'gdlcode'
subnat.columns = ['iso_code', 'country', 'level', 'region']
subnat['is--subnat'] = 'TRUE'
# %%
subnat = subnat.drop(columns=['level'])
# %%
subnat['subnat'] = subnat.index.map(to_concept_id)
# %%
subnat = subnat.reset_index().set_index('subnat')
# %%
subnat['national'] = subnat['iso_code'].map(lambda x: natmap.get(x))
subnat['name'] = subnat['country'].str.strip() + ' - ' + subnat['region'].str.strip()
subnat = subnat.drop(columns=['country', 'region', 'iso_code'])
# %%
subnat.to_csv('../../ddf--entities--level--subnat.csv')
# %%
gs = data.groupby('level')
# %%
data.columns
# %%
gmap = {
    'National': 'national',
    'Poverty': 'poverty',
    'Subnat': 'subnat',
    'Urb/rur': 'urb_rur',
    'Wealth quartiles': 'wealth_quartiles'
}
# %%
for k, df in gs:
    gid = gmap[k]
    dfg = df.copy()
    dfg[gid] = dfg['GDLCODE'].map(to_concept_id)
    dfg = dfg.set_index([gid, 'year']).loc[:, 'sgdi': ]
    for c in dfg.columns:
        cid = to_concept_id(c)
        fname = f'../../datapoints/ddf--datapoints--{cid}--by--{gid}--year.csv'
        ser = dfg[c]
        ser.name = cid
        ser.index.names = [gid, 'year']
        ser.sort_index().dropna().to_csv(fname)
# %%
desc['concept'] = desc['Variable'].map(to_concept_id)
desc = desc.set_index('concept')
desc[['Variable', 'Dtype', 'Shortdescr', 'Longdescr']]
# %%
desc = desc.drop(['country', 'level', 'region', 'continent'])
# %%
desc = desc.drop(columns=['Category', 'Decimals', 'RankOrder', 'Label'])
# %%
desc
# %%
desc.columns = ['name', 'concept_type', 'shortdescr', 'longdescr']
# %%
desc['concept_type'] = 'measure'
# %%
desc.loc[['iso_code', 'gdlcode'], 'concept_type'] = 'string'
desc.loc[['year'], 'concept_type'] = 'time'
# %%
concs = [
    ['level', 'Level', 'entity_domain'],
    ['national', 'National', 'entity_set'],
    ['subnat', 'Sub National', 'entity_set']
]
concs = pd.DataFrame(concs, columns=['concept', 'name', 'concept_type']).set_index('concept')
# %%
concs.loc[['national', 'subnat'], 'domain'] = 'level'
concs.loc[['national', 'subnat'], 'drill_ups'] = 'national'
# %%
concs2 = [
    ['shortdescr', 'Short Description', 'string'],
    ['longdescr', 'Long Description', 'string'],
    ['domain', 'Domain', 'string'],
    ['drill_ups', 'Drill ups', 'string'],
    ['name', 'Name', 'string']
]
concs2 = pd.DataFrame(concs2, columns=['concept', 'name', 'concept_type']).set_index('concept')
# %%
concs3 = [
    ['gnicf', '', 'measure'],
    ['gnicm', '', 'measure'],
    ['mfsel', '', 'measure'],
    ['gnic', '', 'measure'],
]
concs3 = pd.DataFrame(concs3, columns=['concept', 'name', 'concept_type']).set_index('concept')

# %%
cdf = pd.concat([desc, concs, concs2, concs3])
# %%
cdf.to_csv('../../ddf--concepts.csv')
# %%
