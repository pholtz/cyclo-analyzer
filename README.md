# cycloanalyzer
Provides activity metrics in the form of visuals and reports using bulk exports as a data source.

## Usage
Invoking the below command with no arguments or `-h` supplied will yield a list of subcommands and the purpose they serve.

```
$ python cycloanalyzer.py
```

Broadly speaking, the subcommands can be divided into 4 categories.

### Reports
These are configurable report generators which produce standalone html output and as such, are intended to be viewed in a web browser. They operate at a higher level than the commands below, and are composed, in some cases, of many of the below commands. Currently, templating is done through jinja2. Any accompanying css or javascript is internalized into the html for portability. Accompanying visualizations (i.e. plots from the below commands) are embedded into the report as svg.

### Single Ride Metrics
These are pretty straightforward. Using the provided selection criteria, pick the relevant activity and perform analysis.

Generally, most visualizations in this category plot as a function of time, so that you can see changes in an input over the course of the activity.

### Aggregate Metrics
These subcommands visualize over the entire set of activity data provided. These commands are more useful for finding trends over time, such as improvement, patterns, and distributions.

Since these commands look at multiple activities, most visualizations in this category will use activity date as the x axis, and show changes between activities over time. More complex visualizations will relate two or more inputs, which may or may not include activity date.

Generally speaking, these are intended to be run over a set of data spanning months or more.

### Miscellaneous
These subcommands are more utility-based than anything, both operating on and producing data. If specific data manipulations or ahead of time calculations are needed they should be placed here.

For example, the `dump` command can be used to reformat the provided data source to a desired output format. Running `dump` with no arguments will simply print key-value pairs for each activity to stdout.

## Why not use an api?
That data is yours! Free yourself from the constraints of oauth and rate limiting. Export your data when you please, at whatever rate you choose, for your own purposes.
