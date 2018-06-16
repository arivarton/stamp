# workhours
Register work hours in cli.

Stamp in before starting the workday, tag points in time with comments and stamp out when workday is over.

Hours are saved to a sqlite database and exportable to pdf.  


# Environment variables

Name | Default value
:----------------------:|:-------------:
STAMP_MINIMUM_HOURS     | 2  
STAMP_STANDARD_HOURS    | 08:00-16:00  
STAMP_LUNCH             | 00:30  
STAMP_STANDARD_CUSTOMER | Last customer from DB OR create new customer
STAMP_STANDARD_PROJECT  | Last customer from DB OR create new customer
STAMP_WAGE_PER_HOUR     | 300  
STAMP_CURRENCY          | NKR  
STAMP_ORG_NR            | str(Not set)
STAMP_NAME              | str(Not set)
STAMP_ADDRESS           | str(Not set)
STAMP_ZIP_CODE          | str(Not set)
STAMP_ACCOUNT_NUMBER    | str(Not set)
STAMP_PHONE             | str(Not set)
STAMP_MAIL              | str(Not set)

# Install

`python3 setup.py install`

# Usage

### Start worktime
##### With current time
`stamp in -c 'Billed customer' -p 'My project'`
##### With modified time
`stamp in -D 2013-03-03 -T 21:00`


### Tag a point in time
##### With current time
`stamp tag 'My message for the tag'`
##### With modified time
`stamp tag 'My message for the tag' -D 2013-03-03 -T 21:00`


### End worktime
##### With current time
`stamp out`
##### With modified time
`stamp out -D 2013-03-03 -T 21:00`


### Get status of registered and current hours
##### Get status of all registered hours
`stamp status`
##### Get status with filter
Not implemented properly yet.


### Export to pdf
stamp export <month> <year> 
`stamp export jan 2018`


### Delete workday or tags
##### Delete workday
`stamp delete --id 15`
##### Delete tag under workday
`stamp delete --id 15 --tag 3`


### Edit registered or current hours
##### Edit registered hours
`stamp edit --id 15 'customer="My second customer",date="2015-02-02"'`
##### Edit current hours (just remove the id argument)
`stamp edit 'customer="My second customer",date="2015-02-02"'`
##### It is also possible to explicitly declare current hours
`stamp edit --id 'current' 'customer="My second customer",date="2015-02-02"'`


### Edit tags
##### Edit registered tag
`stamp edit --id 15 -t 1 'comment="This is my tag",date="2015-02-02"'`
##### Edit tag under current workday (just remove the id argument)
`stamp edit -t 1 'comment="This is my tag",date="2015-02-02"'`


## Functionality to add
- [ ] Make filter work properly with status using the same options as editing.
- [ ] Trigger mail to customers with pdf invoice.
- [x] Add an boolean option to mark for paid or not paid.
- [ ] Config file.
- [ ] Add to linux distribution package managers starting with Arch Linux.
- [ ] Connect to git.
