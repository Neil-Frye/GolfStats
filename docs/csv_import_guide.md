# CSV Import Guide for GolfStats

This guide will help you prepare your CSV files for importing golf shot data into GolfStats.

## Supported File Format

- Files must be in CSV (Comma Separated Values) format
- The first row must contain column headers
- Each subsequent row represents a single shot
- Text values should not be enclosed in quotes unless they contain commas

## Supported Columns

GolfStats will attempt to map your CSV columns to our database fields automatically. The following column names are recognized:

### Club Information
- `Club`, `Club Type`, `Club Name` → maps to club name in database

### Ball Data
- `Ball Speed`, `Ball Speed (mph)` → maps to ball_speed_mph
- `Club Speed`, `Club Speed (mph)` → maps to club_speed_mph
- `Smash Factor` → maps to smash factor

### Launch Conditions
- `Launch Angle`, `Launch Angle (°)` → maps to launch_angle_degrees
- `Spin Rate`, `Spin Rate (rpm)` → maps to spin_rate_rpm
- `Spin Axis`, `Spin Axis (°)` → maps to spin_axis_degrees
- `Club Path`, `Club Path (°)` → maps to club_path_degrees
- `Face Angle`, `Face Angle (°)` → maps to face_angle_degrees
- `Attack Angle`, `Attack Angle (°)` → maps to attack_angle_degrees

### Distance Measurements
- `Carry`, `Carry (yards)`, `Carry Distance` → maps to carry_distance_yards
- `Total`, `Total (yards)`, `Total Distance` → maps to total_distance_yards
- `Side`, `Side (yards)`, `Side Deviation` → maps to side_deviation_yards
- `Height`, `Height (feet)`, `Apex`, `Apex (feet)` → maps to height_feet

### Other
- `Shot Number` → maps to shot_number
- `Date` → maps to shot_date
- `Notes` → maps to notes

## Automatic Source Detection

GolfStats will automatically attempt to detect if your data is from a specific launch monitor:

### Trackman
Recognizes Trackman exports with headers like: `ClubSpeed`, `BallSpeed`, `SmashFactor`, `LaunchAngle`, etc.

### SkyTrak
Recognizes SkyTrak exports with headers like: `Speed`, `Launch`, `Backspin`, `Carry`, etc.

## Example Format

Here's an example of a properly formatted CSV file:

```
Club,Ball Speed,Club Speed,Smash Factor,Launch Angle,Spin Rate,Carry,Total,Height,Notes
Driver,150.3,110.5,1.36,12.5,2500,245.7,265.2,28.5,Good drive
7 Iron,120.1,85.6,1.40,18.2,6500,155.3,160.5,30.2,Slight draw
```

## Import Steps

1. Navigate to a range session in GolfStats
2. Click the "Import CSV" button
3. Select your CSV file
4. Review the preview of mapped data
5. Confirm the import

## Tips for Successful Imports

- Make sure your numeric values use periods (.) as decimal separators, not commas
- Remove any units from numeric values (e.g., use "150.3" not "150.3 mph")
- If your CSV contains data from multiple clubs, make sure the "Club" column is included
- Any columns not recognized will be ignored during import
- The system will report any unmapped columns after import

## Troubleshooting

If you encounter issues importing your data:

1. Check that your file is properly formatted as a CSV
2. Ensure the first row contains recognizable column headers
3. Verify that numeric values are properly formatted (no text in numeric fields)
4. Try simplifying your column headers to match the supported names above
5. If using data from a launch monitor not listed above, try adjusting your headers to match our default mappings

For persistent issues, contact support with a sample of your CSV file for assistance.