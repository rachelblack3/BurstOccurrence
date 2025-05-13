""" Function for fidning the date string from a datetime object """

def get_date_string(date):
        ''' Method that rpovides date strings
        Outputs:
    
        date_string: string object of date
        year: string object of date year
        month: string object of date month
        day: string object of date day '''

        date_string= str(date.strftime("%Y%m%d"))

        if (date.day <10):
            day = "0"+str(date.day)
        else:
            day = str(date.day)


        if (date.month<10):
            month = "0"+str(date.month)
        else:
            month = str(date.month)
        

        year = str(date.year)
        
        return date_string,year,month,day