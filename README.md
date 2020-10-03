# cycloanalyzer
Provides activity metrics in the form of visuals and reports using bulk exports as a data source.

## Usage
Invoking the below command with no arguments or `-h` supplied will yield a list of subcommands and the purpose they serve.

```
$ python cycloanalyzer.py
```

Broadly speaking, the subcommands can be divided into 3 categories.

### Single Ride Metrics
These are pretty straightforward. Using the provided selection criteria, pick the relevant activity and perform analysis.

Generally, most visualizations in this category plot as a function of time, so that you can see changes in an input over the course of the activity.

### Aggregate Metrics
These subcommands visualize over the entire set of activity data provided. These commands are more useful for finding trends over time, such as improvement, patterns, and distributions.

Since these commands look at multiple activities, most visualizations in this category will use activity date as the x axis, and show changes between activities over time. More complex visualizations will relate two or more inputs, which may or may not include activity date.

Generally speaking, these are intended to be run over a set of data spanning months or more.

### Miscellaneous
These subcommands are more utility-based than anything. If specific data manipulations or ahead of time calculations are needed they should be placed here.

For example, the `dump` command can be used to reformat the provided data source to a desired output format. Running `dump` with no arguments will simply print key-value pairs for each activity to stdout.

## Why not use an api?
That data is yours! Free yourself from the constraints of oauth and rate limiting. Export your data when you please, at whatever rate you choose, for your own purposes.
