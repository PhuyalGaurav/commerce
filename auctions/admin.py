from django.contrib import admin
from .models import Listing, Bid, User , Comment, Watchlist

# Register your models here.
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Watchlist)

admin.site.site_header  =  "Commerce Admin"  
admin.site.site_title  =  "Commerce Admin"
admin.site.index_title  =  "Commerce Admin"