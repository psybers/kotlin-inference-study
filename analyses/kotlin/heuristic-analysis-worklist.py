#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from common.df import *

import pandas as pd

df = get_df('heuristic-identified-calls', 'kotlin', header='infer')

df_sampled = df.sample(n=430).reset_index() \
    .assign(url = lambda df: df.apply(lambda row: f'{row.project}/blob/{row.revision}/{row.file}', axis='columns'),
            is_a = lambda df: '')\
    [['url', 'item', 'called_method', 'identified_as', 'is_a']]

with pd.ExcelWriter('data/manual-evaluation-incomplete.xlsx') as writer:
    df_sampled.style \
        .to_excel(writer, sheet_name='ratings', index=False, freeze_panes=(1, 1))
    for column in df_sampled:
        new_width = min(max(df_sampled[column].astype(str).map(len).max(), len(column)) + 2, 40)
        idx = df_sampled.columns.get_loc(column)
        writer.sheets['ratings'].set_column(idx, idx, new_width)
        if column == 'identified_as':
            writer.sheets['ratings'].set_column(idx, idx, None, None, {'hidden': 1})
