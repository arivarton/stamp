# workhours
Register work hours in cli.

Stamp in before starting the workday, tag points in time with comments and stamp out when workday is over.

Hours are saved to a sqlite database and exportable to pdf.

# Install

`python3 setup.py install`

# Usage

### Start worktime
##### With current time
`stamp add -c 'Billed company'`
##### With modified time
`stamp add -D 2013-03-03 -T 21:00`


### Tag a point in time
##### With current time
`stamp tag 'My message for the tag'`
##### With modified time
`stamp tag 'My message for the tag' -D 2013-03-03 -T 21:00`


### End worktime
##### With current time
`stamp end`
##### With modified time
`stamp end -D 2013-03-03 -T 21:00`


### Get status of registered and current hours
##### Get status of all registered hours
`stamp status`
##### Get status with filter
Not implemented properly yet.


### Export to pdf
Not implemented properly yet.


### Delete workday or tags
##### Delete workday
`stamp delete --id 15`
##### Delete tag under workday
`stamp delete --id 15 --tag 3`


### Edit registered or current hours
##### Edit registered hours
`stamp edit --id 15 'company="My second customer",date="2015-02-02"'`
##### Edit current hours (just remove the id argument)
`stamp edit 'company="My second customer",date="2015-02-02"'`
##### It is also possible to explicitly declare current hours
`stamp edit --id 'current' 'company="My second customer",date="2015-02-02"'`


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


## Database

Workday | Tag
--------|---------
start (datetime) | recorded (datetime)
end (datetime, default=None) | tag (string)
company (string) | workday_id (ForeignKey to Workday id)
tags (OneToMany relationship to Tag) | id_under_workday (integer acting as an id)
