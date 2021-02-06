import os                           # For filepath and directory handling
import pandas as pd                 # Python data analysis and data structures tool
import matplotlib.pyplot as plt     # Python 2D plotting library
import seaborn as sns               # Aesthetic 2D plotting library

# Global constants.
INPUT_DIRECTORY = 'Raw Data'        # Folder name for importing the raw dataset files
DPI = 200                           # Image quality (DPI) for exporting figures

# Load CSV files within directory, and check the directory is not empty
if len(os.listdir(INPUT_DIRECTORY)) == 0:
    print('You have not loaded any raw files for analysis.')

files = []
for file in sorted(os.listdir(INPUT_DIRECTORY)):
    if file.endswith('.csv'):
        files.append(file)
    else:
        print('Script not configured to handle data types other than CSV.')

print('Loaded ' + str(len(files)) + ' files for processing.')

# Create directory to export figures
if not os.path.exists('Figures/'):
    os.mkdir('Figures')

# Defines our controls for statistical calculations
try:
    control_layout = pd.read_csv('control_locations.csv')
except FileNotFoundError as error:
    print('Ensure the plate map is in the script directory.')

# Generate DataFrame with all values from all plates
compiled_df = pd.DataFrame()  # Initialise an empty DataFrame to collate all results per plate
for file in range(len(files)):
    try:
        df = pd.read_csv(INPUT_DIRECTORY + '/' + files[file], skiprows=5)
        df = df.merge(control_layout, how='left', on=['Well Row', 'Well Col']).fillna('COMP')
        df['Plate'] = int(file) + 1
        df.rename(columns={df.columns[3]: 'Raw Absorbance'}, inplace=True)
        compiled_df = compiled_df.append(df)
    except:
        print('File ' + str(files[file]) + ' not processed. Ensure data file is in raw, unedited list format.')

# Function to plot boxplots
def plot_box(title, filename, x='Plate', y='Raw Absorbance', data=compiled_df):
    sns.boxplot(x=x, y=y, data=data, linewidth=0.75, fliersize=0.75)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(('Figures/' + filename + '.png'), dpi=DPI)
    plt.clf()

# Plot boxplot all data, by plate
plot_box('Experiment-wide Raw Absorbances', 'experiment_wide_raw_absorbances')

# Plot experiment-wide row effects
plot_box('Experiment-wide Row Effects', 'experiment_wide_row_effect', x='Well Row')

# Plot experiment-wide column effects
plot_box('Experiment-wide Column Effects', 'experiment_wide_col_effect', x='Well Col')

# Plot barplot of compounds and controls, by plate
sns.catplot(x='COMP_TYPE',
            y='Raw Absorbance',
            hue='Plate',
            data=compiled_df,
            kind='bar',
            height=3,
            aspect=4,
            capsize=.01,
            errwidth=0.6)
plt.xlabel('Compound Type')
plt.ylabel('Raw Absorbance')
plt.title('Raw absorbances by control type')
plt.tight_layout()
plt.savefig('Figures/raw_absorbances_by_control.png', dpi=DPI)
plt.clf()

# Generate DataFrame with control value statistics, by plate
stats_df = compiled_df.groupby(['Plate', 'COMP_TYPE'])['Raw Absorbance'].agg(
    ['mean', 'std', 'median', 'mad']).unstack()
stats_df.columns = [' '.join(col).strip() for col in stats_df.columns.values]  # Flatten hierarchical index

# Regression plot of positive and negative controls
fig, ax = plt.subplots()
sns.regplot(x=stats_df.index, y='mean NEG', data=stats_df, ax=ax)
sns.regplot(x=stats_df.index, y='mean POS', data=stats_df, ax=ax)
plt.ylim(0,240000)
plt.ylabel('Raw Absorbance')
plt.title('Regression plot of control means per plate')
plt.tight_layout()
plt.savefig('Figures/reg_plot_controls.png', dpi=DPI)
plt.clf()

# Calculate signal-to-background (S/B) per plate
stats_df['signal_to_bg'] = (stats_df['mean NEG'] / stats_df['mean POS']).round(2)

# Calculate Z' score per plate
stats_df['Z_factor'] = (1 - (
        (3 * (stats_df['std POS'] + stats_df['std NEG'])) / (stats_df['mean NEG'] - stats_df['mean POS']))).round(3)

# Plot Z' score per plate
sns.barplot(x=stats_df.index, y='Z_factor', data=stats_df)
plt.ylabel("Z' Factor")
plt.axhline(y=0.5, color='#808080', linestyle='--', linewidth=0.75)
plt.title("Z' factor per plate")
plt.annotate(
    ("Average Z' factor = " + str(stats_df['Z_factor'].mean().round(2)) + ", Median Z' factor = " + str(
        stats_df['Z_factor'].median().round(2))),
    (-0.3, 1.2),
    fontsize='x-small',
    color='#808080',
    annotation_clip=False)
plt.tight_layout()
plt.savefig('Figures/Z_factor_bar.png', dpi=DPI)
plt.clf()

# Calculate Z' score robust per plate
stats_df['Z_factor_robust'] = (1 - ((3 * (stats_df['mad POS'] + stats_df['mad NEG'])) / (
        stats_df['median NEG'] - stats_df['median POS']))).round(3)

# Plot Z' Robust per plate
sns.barplot(x=stats_df.index, y='Z_factor_robust', data=stats_df)
plt.ylabel("Robust Z' Factor")
plt.axhline(y=0.5, color='#808080', linestyle='--', linewidth=0.75)
plt.title("Robust Z' factor per plate")
plt.annotate(
    ("Average robust Z' factor = " + str(
        stats_df['Z_factor_robust'].mean().round(2)) + ", Median robust Z' factor = " + str(
        stats_df['Z_factor_robust'].median().round(2))),
    (-0.3, 1.2),
    fontsize='x-small',
    color='#808080',
    annotation_clip=False)
plt.tight_layout()
plt.savefig('Figures/Z_factor_robust_bar.png', dpi=DPI)
plt.clf()
plt.close()

# Export calculate per-plate stats to CSV
stats_df.to_csv('experiment-stats.csv')


# Function to reshape file data into appropriate array and plot to heatmap
def plate_heatmap(file):
    """
    Reshape given raw data file into a 384- or 96-well array and plot to heatmap.
    :param file: an integer value used to reference the files list
    :return: returns seaborn heatmap as png
    """

    global xticks, yticks
    plate = pd.read_csv(INPUT_DIRECTORY + '/' + files[file], skiprows=5)
    plate = plate.iloc[:, 3]

    # Create directory in figures to export heatmaps
    if not os.path.exists('Figures/Heatmaps/'):
        os.mkdir('Figures/Heatmaps')

    if plate.shape[0] == 384:
        plate_reshape = (16, 24)  # number of rows, number of columns for 384
        yticks = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        xticks = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                  '19', '20', '21', '22', '23', '24']
    elif plate.shape[0] == 96:
        plate_reshape = (8, 12)  # number of rows, number of columns for 96
        yticks = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        xticks = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    else:
        print(
            'Unknown plate format - cannot generate the heatmaps. Must be 384 or 96 well format, with no missing values')

    plate_view = plate.values.reshape(plate_reshape)

    sns.heatmap(plate_view,
                yticklabels=yticks,
                xticklabels=xticks,
                square=True,
                vmax=stats_df['median NEG'].median(),  # Normalise upper scale limit across all plates
                cmap='RdBu',
                cbar_kws={'label': 'Raw Absorbance'})
    plt.title('Plate ' + str(file + 1))
    plt.suptitle(str(files[file]))
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.tight_layout()
    plt.savefig('Figures/Heatmaps/heatmap_plate_' + str(file + 1) + '.png', dpi=DPI)
    plt.clf()


# Generate heatmap for every plate in the dataset
for file in range(len(files)):
    plate_heatmap(file)
