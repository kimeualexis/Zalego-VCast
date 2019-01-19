from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from . models import Album, Song
from .forms import UserForm, SongForm, AlbumForm


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']
AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg', 'm4a']


# Create your views here.
@login_required(login_url='musicapp:login_user')
def index(request):
	albums = Album.objects.filter(user=request.user)
	return render(request, 'musicapp/index.html', {'albums': albums})


# Display the details of a particular Album
def detail(request, album_id):
	album = get_object_or_404(Album, pk=album_id)
	return render(request, 'musicapp/detail.html', {'album': album})


# User Registration
def register(request):
	form = UserForm(request.POST or None)
	if form.is_valid():
		user = form.save(commit=False)
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user.set_password(password)
		user.save()
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				albums = Album.objects.filter(user=request.user)
				return render(request, 'musicapp/index.html', {'albums': albums})
	form = UserForm()
	return render(request, 'musicapp/register.html', {'form': form})


# User Login
def login_user(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				albums = Album.objects.filter(user=request.user)
				return render(request, 'musicapp/index.html', {'albums': albums})
			else:
				return render(request, 'musicapp/login.html', {'error_message': 'Account Disabled!'})
		else:
			return render(request, 'musicapp/login.html', {'error_message': 'Invalid Login'})
	return render(request, 'musicapp/login.html')


"""
def user_profile(request, username):
	if request.user.is_authenticated:
		user = User.objects.get(username=username)
		albums = Album.objects.filter(user=request.user)
		return render(request, 'musicapp/profile.html', {'albums': albums, 'user': user})
		"""


# Logout user and redirect to Login page.
def logout_user(request):
	logout(request)
	return redirect('musicapp:login_user')


# Create an Album if user is Authenticated.
def create_album(request):
	if not request.user.is_authenticated:
		return render(request, 'musicapp/login.html')
	else:
		form = AlbumForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			album = form.save(commit=False)
			album.user = request.user
			album.cover = request.FILES['cover']
			file_type = album.cover.url.split('.')[-1]
			file_type = file_type.lower()
			if file_type not in IMAGE_FILE_TYPES:
				context = {
					'album': album,
					'form': album,
					'error_message': 'Image must be PNG, JPG, or JPEG',
				}
				return render(request, 'musicapp/create_album.html', context)
			album.save()
			return render(request, 'musicapp/detail.html', {'album': album})
		form = AlbumForm()
		return render(request, 'musicapp/create_album.html', {'form': form})


# Create a Song.
def create_song(request, album_id):
	form = SongForm(request.POST or None, request.FILES or None)
	album = get_object_or_404(Album, pk=album_id)
	if form.is_valid():
		albums_songs = album.song_set.all()
		for s in albums_songs:
			if s.song_name == form.cleaned_data.get('song_name'):
				context = {
					'album': album,
					'form': form,
					'error_message': 'You Already Added that Song.',
				}
				return render(request, 'musicapp/create_song.html', context)
		song = form.save(commit=False)
		song.album = album
		song.audio_file = request.FILES['audio_file']
		file_type = song.audio_file.url.split('.')[-1]
		file_type = file_type.lower()
		if file_type not in AUDIO_FILE_TYPES:
			context = {
				'album': album,
				'form': form,
				'error_message': 'Audio File must be WAP, MP3 or OGG',
			}
			return render(request, 'musicapp/create_song.html', context)
		song.save()
		return render(request, 'musicapp/detail.html', {'album': album})
	context = {
		'album': album,
		'form': form,
	}
	return render(request, 'musicapp/create_song.html', context)


# Delete an Album.
def delete_album(request, album_id):
	album = get_object_or_404(Album, pk=album_id)
	album.delete()
	albums = Album.objects.filter(user=request.user)
	return render(request, 'musicapp/index.html', {'albums': albums})


# Delete a Song.
def delete_song(request, album_id, song_id):
	album = get_object_or_404(Album, pk=album_id)
	song = Song.objects.get(pk=song_id)
	song.delete()
	return render(request, 'musicapp/detail.html', {'album': album})


#Favorite Song
def favorite(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    try:
        if song.is_favorite:
            song.is_favorite = False
        else:
            song.is_favorite = True
        song.save()
    except (KeyError, Song.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


# Favorite Album
def favorite_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        if album.is_favorite:
            album.is_favorite = False
        else:
            album.is_favorite = True
        album.save()
    except (KeyError, Album.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


#Songs
def songs(request, filter_by):
    if not request.user.is_authenticated:
        return render(request, 'musicapp/login.html')
    else:
        try:
            song_ids = []
            for album in Album.objects.filter(user=request.user):
                for song in album.song_set.all():
                    song_ids.append(song.pk)
            users_songs = Song.objects.filter(pk__in=song_ids)
            if filter_by == 'favorites':
                users_songs = users_songs.filter(is_favorite=True)
        except Album.DoesNotExist:
            users_songs = []
        return render(request, 'musicapp/songs.html', {
            'song_list': users_songs,
            'filter_by': filter_by,
        })