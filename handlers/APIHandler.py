from flask import Blueprint, Response, request, send_from_directory, jsonify
from datetime import datetime, timedelta
import os
from moviepy.editor import VideoFileClip
from urllib.parse import quote
import os.path
import threading
import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs
from fp.fp import FreeProxy

from yt_dlp import YoutubeDL

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

	@api.route( '/crop-video', methods = [ 'GET' ] )
	def crop_video( ):
		try:

			args = request.args

			current_datetime = datetime.now( )
			current_datetime_str = current_datetime.isoformat( )

			video_tmp_directory = './'	

			url_encoded = quote( args[ 'url' ], safe = '' )
			video_yt_filename = 'tmp-yt - {}.mp4'.format( url_encoded )	

			print( '> Downloading' )
			if os.path.exists( '{}/{}'.format( video_tmp_directory, video_yt_filename ) ):
				print( '< Downloading.. done (already downloaded)!' )
			else:

				trying_with_fallback = False
				fallback_worked = False

				try:

					api_url = "https://youtubeslicer.com/download_video"

					parsed_url = urlparse( args['url'] )
					video_id = parse_qs( parsed_url.query )['v'][0]

					api_params = {
						'filename': current_datetime_str,
						'media_type': 'video',
						'video_id': video_id
					}

					api_response = requests.post( url = api_url, json = api_params )

					api_response.raise_for_status( )

					with open( video_yt_filename, "wb" ) as file:
						file.write(api_response.content)					

				except:	

					trying_with_fallback = True
					fallback_worked = False

					print( 'Trying with fallback method (direct YT-DLP call)...' )

					for i in range(5):

						use_random_proxy = ( i > 0 )

						try:

							proxy = FreeProxy( rand = use_random_proxy, https=True, url="www.youtube.com" ).get( )
							print( 'Proxy:' )
							print( proxy )

							ydl_opts = { 
								"format": "best[ext=mp4]",
                                "outtmpl": os.path.join(video_tmp_directory, video_yt_filename),
								"proxy": proxy,
								"extractor_retries": 1
							}						
							with YoutubeDL( ydl_opts ) as ydl:
								ydl.download( [ args[ 'url' ] ] )
								fallback_worked = True
								print( 'Successfully downloaded through proxy!' )
								break

						except Exception as e:
							print( e )

				if trying_with_fallback == True and fallback_worked == False:
					fallback_failed_msg = 'Not working at the moment, please try again later!'
					print( fallback_failed_msg )
					return Response( fallback_failed_msg, status = 500 )							

				print( '< Downloading.. done!' )			

			video_output_filename = 'YTC - {}.mp4'.format( current_datetime_str )	
			video_ffmpeg_filename = 'tmp-ff - {}'.format( video_output_filename )		

			start_datetime = datetime.strptime( args[ 'start_time' ], "%M:%S" )
			start_timedelta = start_datetime - datetime( 1900, 1, 1 )
			start_time_in_seconds = start_timedelta.total_seconds( )

			end_datetime = datetime.strptime( args[ 'end_time' ], "%M:%S" )
			end_timedelta = end_datetime - datetime( 1900, 1, 1 )
			end_time_in_seconds = end_timedelta.total_seconds( )		

			print( '> Cutting' )
			clip = VideoFileClip( video_yt_filename ).subclip( start_time_in_seconds, end_time_in_seconds )
			clip.write_videofile( filename = video_ffmpeg_filename, codec = "libx264", temp_audiofile = 'temp-audio.m4a', remove_temp = True, audio_codec = 'aac' )		
			clip.close( )
			print( '< Cutting' )		

			print( '> Preparing request' )	
			succ_response = send_from_directory( video_tmp_directory, path = video_ffmpeg_filename, as_attachment = True  )
			succ_response.headers[ 'Content-Disposition' ] = "attachment; filename={};".format( video_output_filename )
			succ_response.headers[ 'Access-Control-Expose-Headers' ] = 'Content-Disposition'
			print( '< Preparing request' )		

			print( '!! DONE !!' )	

			return succ_response

		except Exception as e:

			return Response( str( e ), status = 500 )