class UserAccessInvoiceNoReadException(Exception):
    def __init__(self):
        super().__init__("User account does not have Read Permissions" +
                         " for Invoices. Please contact your administrator.")

class UserAccessInvoiceNoEditException(Exception):
    def __init__(self):
        super().__init__("User account does not have Edit Permissions" +
                         " for Invoices. Please contact your administrator.")

class UserAccessDocketNoReadException(Exception):
    def __init__(self):
        super().__init__("User account does not have View Permissions" +
                         " for Dockets. Please contact your administrator.")

class UserAccessDocketNoEditException(Exception):
    def __init__(self):
        super().__init__("User account does not have Edit Permissions" +
                         " for Dockets. Please contact your administrator.")

class UserAccessDocketNoAdminException(Exception):
    def __init__(self):
        super().__init__("User account does not have Admin Privaleges" +
                         " for Dockets. Please contact your administrator.")

class UserAccessInvoiceNoAdminException(Exception):
    def __init__(self):
        super().__init__("User account does not have Admin Privaleges" +
                         " for Invoices. Please contact your administrator.")

class UserAccessInvoiceNoApproveException(Exception):
    def __init__(self):
        super().__init__("User account does not have Approver Status" +
                         " for Invoices. Please contact your administrator.")

class UserAccessNotSignedInException(Exception):
    def __init__(self):
        super().__init__("You are not signed in. " +
                         "Please sign in, and try again.")

class UserAccessInvalidTokenException(Exception):
    def __init__(self):
        super().__init__("Could not validate token. " +
                         "Unable to reset password.")
