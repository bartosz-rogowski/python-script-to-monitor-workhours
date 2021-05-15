# Python script to monitor workhours

## Environment preparation

In order to run script, environment with proper dependencies has to be created.

`python -m pip install -r requirements.txt`

- Anaconda Users

`conda env create -n <env name> -f env.yml`

## How to run the script

`python swi.py [-h] [-p PATH] [-rn RESULT_NAME]`

Flags:
- `-h` or `--help` - displays help and short description
- `-p` or `--path` - path to csv file (default set to *input.csv*)
- `-rn` or `--result_name` - name (and extension) of the result file (default set to *result*)

## Project description

The main task of the script is to monitor working hours that are included in csv file (default in *input.csv*).
That file has to contain 3 columns: 
- **Date** - date and time of the event
- **Event** - event (*Reader entry* or *Reader exit*)
- **Gate** - id of the door

The results will be included in file *result* (unless user specifies it) and will contain information about:
- amount of time spend in building in a day
- literal:
  - **w** if the day is a weekend
  - **ot** if working time is grater than specified time (9 hours)
  - **ut** if working time is less than specified time (6 hours)
  - **i** if time is inconclusive
- next to every last day of the week there will be summary of summaric time spent in the building and the overtime.

## Additional information

All constants are provided in *constants.py* so that they could be easily changeable.

All necessary functions are icnluded in *lib.py*.

The main script is *swi.py* 
