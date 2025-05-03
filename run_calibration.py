#!.venv/bin/python
import argparse
import pprint
from colorama import Fore,Back,Style
import yaml
from internal.cal_cl import Cal
import pickle

parser = argparse.ArgumentParser(description="To create the calibrations files\nyou can use the default assets\nbut the results depends of the terminal fonts and colors\nis better generate your own calibration")
parser.add_argument("output_file",         help="name of the output file (will be store at /calibration dir) ")            # positional argument
parser.add_argument("-c", "--color_config_file",  help="Color sets", default="calibrations/colorset_default.yaml")             # optional argument
#parser.add_argument("-v", "--verbose",     action="store_true", help="Enable verbose mode")  # flag
parser.add_argument("-s", "--screen",       help="Screen number to perform the calibration",default=1)
args = parser.parse_args()

print(f" - opening color config: {args.color_config_file} - ")
with open(args.color_config_file, "r") as f:
    color_config = yaml.safe_load(f)

cal = Cal(args,color_config)
cal.print_and_capture_reference_page()
n_pages = cal.get_number_of_pages()
for n in range(n_pages):
    cal.print_next_page_and_capture()

if not str(args.output_file).startswith("calibrations/"):
    args.output_file = f"calibrations/{args.output_file}"
print(f" - dumping to: {args.output_file} - ")
file = open(args.output_file, 'wb')
pickle.dump(cal.get_calibration_dict(), file)
file.close()


