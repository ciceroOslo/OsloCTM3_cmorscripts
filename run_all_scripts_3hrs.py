import subprocess


print('Run script for 3 hourly output')

# List of Python scripts to run
scripts = ["write_hywayoutput_3hrs_airmass.py",
           "write_hywayoutput_3hrs_pfull_height.py",
           "write_hywayoutput_3hrs_vmr.py"]


for script in scripts:
    try:
        # Run the script
        result = subprocess.run(["python", script], check=True, capture_output=True, text=True)
        
        print(f"Output of {script}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e.stderr}")
