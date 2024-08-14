#!/usr/bin/env python
# coding: utf-8

# %% build the dataframe
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from common.graphs import setup_plots, save_figure
from common.local import *
from common.tables import *
from common.df import *
import pandas as pd
import matplotlib.ticker as mtick

import scipy.stats as stats

df_tests = get_df('tests', 'kotlin', header='infer') \
    .assign(is_test = True)

df_orig = get_df('basic-usage', 'kotlin', header='infer')
df = df_orig.merge(df_tests, how='left', on=['project', 'file'])
df['is_test'] = df.is_test.fillna(False)

df_totals = df.groupby(['project', 'is_test', 'location'])[['count']].sum().rename(columns={'count':'total'}).reset_index()

df_counted = df.groupby(['project', 'location', 'is_test', 'isinferred'], as_index=False).sum()[['project', 'location', 'isinferred', 'is_test', 'count']]

df_temp = pd.merge(pd.merge(pd.merge(pd.Series(df_counted.project.unique(), name='project'),
                                     pd.Series(df_counted.location.unique(), name='location'), how='cross'),
                            pd.Series(df_counted.isinferred.unique(),name='isinferred'), how='cross'),
                   pd.Series(df_counted.is_test.unique(), name='is_test'), how='cross')

df_counted = df_counted.merge(df_temp,
                              on=['project', 'location', 'isinferred', 'is_test'],
                              how='right') \
                       .fillna(0)

print(df_counted.head())
                              

df_summarized = df_counted.merge(
    df_totals,
    on=['project', 'is_test', 'location'],
    how='outer')

print(df_summarized.head())
df_summarized = df_summarized[df_summarized.total > 0]

df_summarized['percent'] = df_summarized.apply(
    lambda x: 0 if x['total'] == 0 else (x['count'] / x['total']) * 100,
    axis=1)
df_summarized['isinferred'] = df_summarized['isinferred'].apply(inferred_name)
df_summarized['location'] = df_summarized['location'].apply(location_map)

summarized = df_summarized

# %% generate the plot
fig, ax = setup_plots()

sns.boxplot(x='location',
            y='percent',
            hue='isinferred',
            hue_order=['Inferred', 'Not Inferred'],
            data=summarized.loc[summarized.is_test],
            ax=ax,
            order=location_order,
            showfliers=False)

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylabel('Percent per Project')
ax.set_xlabel('')
ax.get_legend().set_title('')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)
save_figure(fig, 'rq-usage-tests.pdf', subdir='kotlin')
fig

# %% generate the table
data = summarized.loc[summarized.is_test][['location', 'isinferred', 'percent']].groupby(['location', 'isinferred']).describe()
styler = highlight_cols(highlight_rows(get_styler(drop_count_if_same(drop_outer_column_index(data)))))

save_table(styler, 'rq-usage-tests.tex', subdir='kotlin')

# %% run ANOVAs

results = []

for location in ['Return\nType', 'Local\nVariable', 'Global\nVariable', 'Lambda\nArgument', 'Field', 'Loop\nVariable']:
    for inferred in ['Inferred', 'Not Inferred']:
        result = stats.kruskal(summarized.loc[((summarized.location == location) & (summarized.isinferred == inferred) & summarized.is_test), 'percent'],
                               summarized.loc[((summarized.location == location) & (summarized.isinferred == inferred) & ~summarized.is_test), 'percent'])
        results.append({'Location': location,
                        'Inferred?': inferred,
                        'H': result.statistic,
                        'p': result.pvalue })

results_df = pd.DataFrame(results).set_index(['Location', 'Inferred?'])

styler = highlight_cols(highlight_rows(get_styler(results_df)))

save_table(styler, 'rq-tests-differences.tex', subdir='kotlin', decimals=4)

