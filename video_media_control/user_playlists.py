@check_internet
def get_user_playlists_thread(mode):#0 = normal fun, 1 = init fun
    '''
    To get wat playlist do user have
    mode 0 = normal fun, 1 = init fun
    '''

    try:
        if not youtube:youtube = build('youtube','V3',developerKey=youtubeAPI,static_discovery = False,credentials=credentials)
    except Exception as e:ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))
    try:
        global playlists
        playlists = youtube.playlists().list(part='snippet', mine=True,maxResults=500).execute()
    except:
        try:
            if not youtube:youtube = build('youtube','V3',developerKey=youtubeAPI,static_discovery = False,credentials=credentials)
            playlists = youtube.playlists().list(part='snippet', mine=True,maxResults=500).execute()
        except Exception as e:ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))

    try:
        for playlist in playlists['items']:
            user_playlists_id.append(f"{playlist['id']}")
            user_playlists_name.append(f"{playlist['snippet']['title']}")
        if mode == 0:
            ui_queue.put(lambda: userplaylistcombobox.configure(values=user_playlists_name))
            ui_queue.put(lambda: userplaylistcombobox._open_dropdown_menu())
        elif mode == 1:
            try:
                ui_queue.put(lambda: init_playlist_combobox.configure(values=user_playlists_name))
                ui_queue.put(lambda: init_playlist_combobox.event_generate('<Button-1>'))
                init_playlists_id = user_playlists_id
            except:pass

    except Exception as e:log_handle(content=str(e))




@check_internet
def get_youtube_playlist_thread(playlistid_input = None): 
    '''
    playlistid_input is used for quick init function, it will directly use the playlist id from the input instead of the global playlistID variable, which is set when user select a playlist from the combobox
    
    '''
    ###### get specifc info from the playlist that user choose
    global loadingplaylist,selected_song_number,playlistID,media_data_list
    loadingplaylist = True
    try:
        selected_song_number = None
        playlistsongs =  []
        media_data_list.playlisttitles.clear()
        media_data_list.playlist_channel.clear()
        media_data_list.playlist_thumbnails.clear()
        media_data_list.vid_url.clear()
        nextpagetoken = None

        ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
        ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
        if youtube == None:
            google_control.get_cred()
            ui_queue.put(lambda: google_status_update())
            get_user_playlists(0)
        elif playlistID.get() or playlistid_input:
            ui_queue.put(lambda: playlistlabel.configure(text='⏳'))
            while True:
                playlist_response = youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlistID.get() if not playlistid_input else playlistid_input,
                    maxResults=100,
                    pageToken=nextpagetoken
                ).execute()
                playlistsongs.extend(playlist_response['items'])
                nextpagetoken = playlist_response.get('nextPageToken')
                if not nextpagetoken:
                    break
            tree_index = 1
            for item in playlistsongs:
                try:
                    video_id = item['contentDetails']['videoId']
                    title_response = youtube.videos().list(
                        part='snippet',
                        id=video_id
                    ).execute()
                    media_data_list.vid_url.append(f"https://www.youtube.com/watch?v={video_id}")
                    vid_info = title_response['items'][0]['snippet']
                    media_data_list.playlist_channel.append(vid_info['channelTitle'])
                    media_data_list.playlisttitles.append(vid_info['title'])
                    media_data_list.playlist_thumbnails.append(vid_info['thumbnails']['high']['url'])
                    insert_treeview_quene.put((vid_info['thumbnails']['high']['url'],vid_info['title'],vid_info['channelTitle']))
                    tree_index += 1
                except Exception as e:
                    log_handle(content=str(e))

        

    except googleapiclient.errors.HttpError as err: ######  handle stupid api
            ui_queue.put(lambda e=err: messagebox.showerror(f'JaTubePlayer {ver}', f"An error occurred: {e}"))
    except Exception as e:
            ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', err))
    ui_queue.put(lambda: playlistlabel.configure(text='📁'))
    ui_queue.put(lambda: page_num_label.configure(text=''))
    loadingplaylist = False