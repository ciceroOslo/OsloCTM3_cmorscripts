import subprocess

# List of Python scripts to run
scripts = ["write_hywayoutput_airmass.py",
           "write_hywayoutput_height.py",
           "write_hywayoutput_gridarea.py",
           "write_hywayoutput_surface_altitude.py",
           "write_hywayoutput_temperature.py",
           "write_hywayoutput_pressure.py",
           "write_hywayoutput_chemprodloss.py",
           "write_hywayoutput_drydep.py",
           "write_hywayoutput_emissions.py",
           "write_hywayoutput_mmr.py",
           "write_hywayoutput_vmr.py",
           "write_hywayoutput_wetdep.py",
           "write_hywayoutput_lightning_emissions_3d.py"]


for script in scripts:
    try:
        # Run the script
        result = subprocess.run(["python", script], check=True, capture_output=True, text=True)

        print(f"Output of {script}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e.stderr}")
