% Load TIF file
[data, R] = readgeoraster("C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step2TernaryChange\PurecwmapTernaryChange\PurecwmapTernaryChange2006to2010.tif");

disp(unique(data(:))) % Helps to find what classes we have and if there are any no data classes inflating the size of the file

% Define your valid change classes (exclude 255)
valid_classes = [1, 2, 3, 4, 5, 6, 7];

% Create mask to exclude NoData
valid_mask = data ~= 255;

% Now proceed with stratified sampling on valid pixels only
class_counts_valid = [1.2836e+08, 2.1493e+07, 1.5567e+08, 80328, 6.8788e+05, 55270, 1.3014e+06]; % This was found via the attribute table of the septenary change file (titled ternary change because I was too lazy to change the name), or via using some matlab code i can't find anymore 
total_valid_pixels = sum(class_counts_valid);

% Calculate proportions (excluding NoData)
class_props = class_counts_valid / total_valid_pixels;

% Set your sampling parameters
min_samples_rare = 100;  % minimum for rare classes (4, 6)
total_samples = 2000;    % adjust as needed

% Calculate samples per class
samples_per_class = round(total_samples * class_props);

% Ensure rare classes (4 and 6) get minimum samples
samples_per_class(5) = max(samples_per_class(5), min_samples_rare);
samples_per_class(7) = max(samples_per_class(7), min_samples_rare);
samples_per_class(4) = max(samples_per_class(4), min_samples_rare); % Class 4
samples_per_class(6) = max(samples_per_class(6), min_samples_rare); % Class 6

disp('Samples per class:');
for i = 1:length(valid_classes)
    fprintf('Class %d: %d samples\n', valid_classes(i), samples_per_class(i));
end

% Now do the actual sampling
sample_coords = [];
sample_values = [];

for i = 1:length(valid_classes)
    class_val = valid_classes(i);
    n_samples = samples_per_class(i);

    % Find pixels of this class (excluding NoData)
    class_mask = (data == class_val) & valid_mask;
    [row_idx, col_idx] = find(class_mask);

    if length(row_idx) >= n_samples
        selected_idx = randsample(length(row_idx), n_samples);
        sample_coords = [sample_coords; row_idx(selected_idx), col_idx(selected_idx)];
        sample_values = [sample_values; repmat(class_val, n_samples, 1)];
    else
        % Use all available if fewer than requested
        sample_coords = [sample_coords; row_idx, col_idx];
        sample_values = [sample_values; repmat(class_val, length(row_idx), 1)];
    end
end

fprintf('Total samples collected: %d\n', length(sample_values));

% Load your second map
[map2, ~] = readgeoraster("C:\Users\kamrmo24\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step2TernaryChange\PureCCAPTernaryChange\PureCCAPTernaryChange2006to2010.tif");

% Extract values from second map at sample locations
map2_values = map2(sub2ind(size(map2), sample_coords(:,1), sample_coords(:,2)));

% Remove any samples that hit NoData in either map
valid_samples = (sample_values ~= 255) & (map2_values ~= 255);
map1_clean = double(sample_values(valid_samples));
map2_clean = double(map2_values(valid_samples));

% Create confusion matrix
C = confusionmat(map2_clean, map1_clean);

% Create confusion chart with proper labels and totals
figure;
confusionchart(map2_clean, map1_clean, ...
    'Title', 'Confusion Matrix: cwmap2006to2010 vs CCAP2006to2010', ...
    'XLabel', 'cwmap2006to2010 (Test)', ...
    'YLabel', 'CCAP2006to2010 (Reference)', ...
    'RowSummary', 'row-normalized', ...
    'ColumnSummary', 'column-normalized');

% Display with labels
valid_classes = [1, 2, 3, 4, 5, 6, 7];
