from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .forms import ListingForm 
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Bid, Comment, Watchlist

def error(request, msg):
    msg = msg
    return render(request, 'auctions/error.html',{
        'msg' : msg,
        "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
    })
    




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication sucessful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url="/login")   
def listit(request):
    if request.method == "POST":
        form = ListingForm(request.POST)

        if  form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            stbid = form.cleaned_data['starting_bid']
            photo = form.cleaned_data['image_url']
            category = form.cleaned_data['category']
            price = form.cleaned_data['price']
            starting_bid = form.cleaned_data['starting_bid']
            db = Listing(user=request.user,title=title,description=description, starting_bid=stbid, image_url=photo, category=category, price=price)
            db.save()
            return error(request, 'Sucessfully Listed!!')
        else:
            return error(request, "Form Not Valid !")


    else:
        form = ListingForm()
        return render(request,'auctions/listingform.html',{
            "form" : form,
            "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
        })


def index(request):

    return render(request, "auctions/index.html",{
        "listings" : Listing.objects.all(),
        "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
    })

def listitem(request, listitem , message="", message_type=""):
    listing = Listing.objects.get(pk=listitem)
    try:
        bid = Bid.objects.get(user=listing.user.username)
    except:
        bid = 0
    user = request.user
    comment = Comment.objects.filter(auction=listing)
    try:
        ide = Watchlist.objects.get(user=request.user)
        if listing.id == ide.listingid:
            show_remove = "True"
        else:
            show_remove = "False"
    except:
        show_remove = "False"
    return render(request, "auctions/listitem.html",{
        "listings" : listing,
        "bids" : bid,
        "user" : user,
        "comment" : comment,
        "added" : show_remove,
        "message" : message,
        "msg_type" : message_type,
        "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
    })


@login_required(login_url="/login")  
def watchlist(request):
    lists = Watchlist.objects.filter(user=request.user.username)
    prodlst = []
    if lists:
        present = True
        for item in lists:
            product = Listing.objects.get(id=item.listingid)
            prodlst.append(product)
    return render(request, "auctions/watchlist.html" ,{
        "listings" : prodlst,
        "list" : [],
        "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
    }) 


@login_required(login_url="/login")  
def watchlistadd(request, listid):
    cnt = 0
    obj = Watchlist.objects.filter(listingid=listid, user=request.user)
    if obj:
        obj.delete()
        # return error(request, "Sucessfuly Removed")
    else:
        db = Watchlist(user=request.user, listingid=listid, counter=cnt)
        db.save()
        # return error(request, "Sucessfuly Added")
    return HttpResponseRedirect(reverse("listitem", args=(listid, )))
    
def categories(request):
    lists = Listing.objects.values_list('category', flat=True).distinct()
    list2 = []
    for i in lists:
        if i != "":
            list2.append(i)
    return render(request, "auctions/categories.html",{
        "categories" : list2,
        "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
    })

def categorieslist(request, category):
    
    lists = Listing.objects.filter(category=category)
    if lists.count() == 0:
        return error(request, "Nothing added in this category")
    # try:
    #     lists = Listing.objects.filter(category=category)
    # except:
    #     lists = []
    return render(request, "auctions/watchlist.html" ,{
        "listings" : lists,
        "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
    }) 

@login_required(login_url="/login")   
def addbid(request, listid):
    if request.method == "POST":
        newbid = int(request.POST.get("newbid"))
        item = Listing.objects.get(pk=listid)
        if item.price >= newbid:
            return listitem(request, listid, "Bid Was Not Added :( (probably bid lower than the before bid :( )", "danger")
        else:
            item.price = newbid
            item.save()
            bidToDb = Bid(user=request.user, amount=newbid, auction=item)
            bidToDb.save()
            return listitem(request, listid, "Bid successfully added!", "success")

    else:
        return error(request, "Wrong place kiddo ;)")

@login_required(login_url="/login")
def addcomment(request, listid):  
    if request.method == "POST":
        comment = request.POST.get("comment")
        item = Listing.objects.get(pk=listid)
        Comment(user=request.user, auction=item, text=comment).save()
        return listitem(request, listid, "Your comment was added! ", "success")
    else:
        return error(request, "Wrong place kiddo ;)")

@login_required(login_url="/login")
def closebid(request, listid):
    auction = get_object_or_404(Listing, id=listid)
    if request.user == auction.user:
        auction.active, auction.winner = False, request.user.username
        auction.save()
    else:
        return error(request, "Not your Bid to close !")
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url="/login")
def winnings(request):

    wins = Listing.objects.filter(winner=request.user.username)
    return render(request, "auctions/winnings.html", {
        "listings" : wins,
        "list" : [],
        "no_watchlist" : len(Watchlist.objects.filter(user=request.user))
    })