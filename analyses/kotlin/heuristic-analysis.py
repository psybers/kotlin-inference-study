#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from common.df import *

import pandas as pd

import statsmodels.stats.inter_rater as irr

df_data = get_df('heuristic-identified-calls', 'kotlin', header='infer') \
    .assign(url = lambda df: df.apply(lambda row: f'{row.project}/blob/{row.revision}/{row.file}', axis='columns'))

df_ratings = pd.read_excel('data/manual-evaluation-complete.xlsx') \
    .drop(columns = ['identified_as'])
df_ratings = df_ratings.drop(columns = [ col for col in df_ratings.columns if col.startswith('Unnamed') ]).dropna()

df = pd.merge(df_ratings, df_data, how='left', on=['url', 'item', 'called_method']) \
    [['url', 'item', 'called_method', 'identified_as', 'is_a']]

df['is_equal'] = df.identified_as.eq(df.is_a)


print(100 * df.is_equal.sum() / len(df.is_equal))

table, dims = irr.to_table(df[['identified_as', 'is_a']])
print(table)
print(irr.cohens_kappa(table))
