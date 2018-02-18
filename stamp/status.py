from db import query_for_workdays, current_stamp
from helpers import output_for_total_hours_date_and_wage


def print_status(args):
    workdays = query_for_workdays(args=args)
    for workday in workdays:
        output_total_hours, output_date, output_total_wage = output_for_total_hours_date_and_wage(workday)
        print('id: %d' % workday.id)
        print(output_date)
        print('Company: %s' % workday.company)
        print('Workday: ')
        print('%s-%s' % (workday.start.time().isoformat(),
                         workday.end.time().isoformat().split('.')[0]))
        print('Hours: %s@%s' % (output_total_hours, output_total_wage))
        print('%d tag(s)' % len(workday.tags.all()))
        for tag in workday.tags:
            print('\t[id: %d] [Tagged: %s | %s]\n\t%s' % (tag.id_under_workday, tag.recorded.date().isoformat(), tag.recorded.time().isoformat(), tag.tag))
        print('--')
    output_total_hours, __, output_total_wage = output_for_total_hours_date_and_wage(workdays)
    print('Total hours: %s' % output_total_hours)
    print('Total wage earned: %s' % output_total_wage)


def print_current_stamp():
    stamp = current_stamp()
    if stamp is not None:
        print('\n\nCurrent stamp:')
        print('%s %s' % (stamp.start.date().isoformat(), stamp.start.time().isoformat().split('.')[0]))
        print('Company: %s' % stamp.company)
        print('%d tag(s):' % len(stamp.tags.all()))
        for tag in stamp.tags:
            print('\t[id: %d] [Tagged: %s | %s]\n\t%s' % (tag.id_under_workday, tag.recorded.date().isoformat(), tag.recorded.time().isoformat(), tag.tag))
        print('')
    else:
        print('\nNot stamped in.')
