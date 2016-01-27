Python 3 script to clean up XML downloaded from SwissMedic (AIPS).

## Usage

Make sure you have Python 3 installed and all modules listed in `requirements.txt`.
The suggested way is to use virtualenv:

```bash
cd medication-cleaner
virtualenv -p python3 env
. env/bin/activate
pip install -r requirements.txt
```

Then download the archive from <http://download.swissmedicinfo.ch> by clicking “I accept” » “Ja”.
Expand it and place the resulting XML into the same directory, naming it `Download.xml`.

Start the script:

```bash
./parse.py
```

The cleaned XML gets written to the same directory with the name `Cleaned.xml`.
The script will run for a while; you'll see how many of the roughly 22'000 medications the script has already processed.
