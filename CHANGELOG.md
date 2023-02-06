## v14.0.0 (2023-02-05)

## v13.0.2 (2023-01-16)

## v13.0.1 (2022-12-27)

## v13.0.0 (2022-10-18)

### Fix

- moved to breaking change toolbox_utils where replaced typical with pydantic
- hopefully this change will install message.wdm into the correct place on windows and mac

## v12.9.5 (2022-10-04)

### Fix

- if using "x.wdm,1" would bring the time-series in twice
- need to support python 3.7 onward

## v12.9.4 (2022-06-15)

### Refactor

- remove __future__ and f strings

### Fix

- **pyproject.toml**: forgot to manually edit the version number again

## v12.9.3 (2022-05-17)

### Fix

- **tsfill**: corrected to match previous behavoir where read_dsn defaulted tsfill to -999
- pip_requirements.txt to reduce vulnerabilities

## v12.9.2 (2022-04-17)

## v12.9.1 (2022-03-28)

### Fix

- **describe_dsn**: removed pseudo attributes "llsdat", "lledat", "DSN", ...etc. from being requested from new describe_dsn attrs keyword
- **listdsns**: attribute keys changed in listdsns to match what is created in describe_dsn

## v12.9.0 (2022-03-25)

### Fix

- **describedsn**: uppercased required keywords to match what is returned by describedsn
- deletes a half-built DSN

### Feat

- **attributes**: added ability to get and set DSN attributes

## v12.8.2 (2022-02-14)

### Fix

- fixed tstoolbox version dependency to use tz_localize or tz_convert on Timestamps as needed

## v12.8.1 (2022-02-14)

## v12.8.0 (2021-08-06)

## v12.7.2 (2021-08-02)

## v12.7.1 (2021-08-02)

## v12.7.0 (2021-07-28)

## v12.6.0 (2021-06-29)

### Refactor

- Implement all edits from .pre-commit-config.yaml

## v12.5.0 (2021-05-12)

### Fix

- Work with latest tstoolbox.

## v12.4.0 (2021-03-14)

### Fix

- Add complete drug/dealings.

## v12.2.0 (2021-03-10)

### Fix

- Fix for building wdm lib.

## v12.0.0 (2020-04-30)

## v11.13.12.8 (2019-11-07)
