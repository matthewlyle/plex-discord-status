#!/usr/bin/env python3
"""
Plex Discord Status - Discord Rich Presence for Plex Media Server
A simple script to show what you're watching on Plex in your Discord status. See README for limitations.
"""

import time
import configparser
import sys
from plexapi.server import PlexServer
from pypresence import Presence

def load_config():
    """Load configuration from file"""
    config = configparser.ConfigParser()
    if not config.read('config.ini'):
        print("[ERROR] 'config.ini' was not found. Please make sure it is present in the app folder.")
        sys.exit(1)
    
    try:
        return {
            'plex_url': config['plex']['url'],
            'plex_token': config['plex']['token'],
            'plex_username': config['plex']['username'],
            'discord_client_id': config['discord']['client_id'],
            'poll_interval': int(config.get('app', 'interval', fallback='30').strip().split('#')[0].strip())
        }
    except KeyError as e:
        print(f"[ERROR] Missing config value: {e}")
        sys.exit(1)

def connect_discord(client_id):
    """Connect to Discord, retrying if necessary"""
    while True:
        try:
            rpc = Presence(client_id)
            rpc.connect()
            print("Connected to Discord")
            return rpc
        except Exception:
            print("[WARN] Discord not detected. Waiting for Discord to start...")
            time.sleep(10)

def get_session_info(session, username):
    if session.type == "episode":
        series = getattr(session, 'grandparentTitle', '')
        episode_title = getattr(session, 'title', '')
        episode = f"S{getattr(session, 'parentIndex', 0):02}E{getattr(session, 'index', 0):02}"
        details = f"Watching {series}"
        state = f"{episode_title} ({episode})"
        print(f"[OK] {username} is watching {series}: {episode_title} ({episode})")
        
    elif session.type == "movie":
        movie_title = getattr(session, 'title', '')
        details = f"Watching {movie_title}"
        print(f"[OK] {username} is watching {movie_title}")
        
    elif session.type == "track":
        song_title = getattr(session, 'title', '')
        artist = getattr(session, 'parentTitle', '')
        album = getattr(session, 'grandparentTitle', '')
        details = f"Listening to {song_title} by {artist}"
        state = album
        print(f"[OK] {username} is listening to {song_title} by {artist} ({album})")
        
    else:
        details = f"Watching: {getattr(session, 'title', '')}"
        state = session.type.capitalize()
        print(f"[OK] {username} is watching {getattr(session, 'title', '')}")
    
    return details, state

def main():
    try:

        config = load_config()
        
        plex = PlexServer(config['plex_url'], config['plex_token'])
        print(f"Connected to Plex server @ {config['plex_url']}")
        
        rpc = connect_discord(config['discord_client_id'])
        
        print("Plex Discord Status is running. Press Ctrl+C to stop.")
        
        while True:
            try:
                sessions = plex.sessions()
                watching = None

                # Find user's session
                for session in sessions:
                    if session.usernames[0] == config['plex_username']:
                        watching = session
                        break

                # Update Discord status
                if watching:
                    details, state = get_session_info(watching, config['plex_username'])
                    rpc.update(
                        details=details,
                        state=state,
                        large_image="logo",
                        large_text="Plex",
                        start=int(time.time())
                    )
                else:
                    rpc.clear()
                    print(f"[OK] {config['plex_username']} is not watching anything.")

                time.sleep(config['poll_interval'])
                
            except Exception as e:
                print(f"[WARN] Error: {e}. Retrying in 10 seconds...")
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("\nStopping...")
        if 'rpc' in locals():
            rpc.clear()
        print("Stopped and cleared status.")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 