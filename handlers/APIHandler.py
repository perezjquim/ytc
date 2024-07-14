from flask import Blueprint, Response, request, send_from_directory, jsonify
from datetime import datetime, timedelta
from yt_dlp import YoutubeDL
import os
from moviepy.editor import VideoFileClip
from fp.fp import FreeProxy
from urllib.parse import quote
import os.path
import threading


api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	__proxies_lock = None
	__proxies = None

	def get_blueprint( self ):
		return api	

	@api.route( '/crop-video', methods = [ 'GET' ] )
	def crop_video( ):
		try:

			args = request.args

			current_datetime = datetime.now( )
			current_datetime_str = current_datetime.isoformat( )

			video_tmp_directory = './'	

			url_encoded = quote( args[ 'url' ], safe = '' 	)
			video_ydl_filename = 'tmp-ydl - {}.mp4'.format( url_encoded )	

			print( '> Downloading' )
			if os.path.exists( '{}/{}'.format( video_tmp_directory, video_ydl_filename ) ):
				print( '< Downloading.. done (already downloaded)!' )
			else:
				ydl_opts = { "format": "b[filesize<50M]", "outtmpl": video_ydl_filename }
				with YoutubeDL( ydl_opts ) as ydl:
						ydl.download( [ args[ 'url' ] ] )			
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
			clip = VideoFileClip( video_ydl_filename ).subclip( start_time_in_seconds, end_time_in_seconds )
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

	@api.route( '/get-video-info', methods = [ 'GET' ] )
	def get_video_info( ):
		try:
			
			args = request.args

			with YoutubeDL({}) as ydl:
					video_info = ydl.extract_info( args[ 'url' ], download = False )
					title = video_info.get( 'title' )
					thumbnail_url = video_info.get( 'thumbnails' )[ 0 ][ 'url' ]
					author = video_info.get( 'uploader' )
					duration = str( timedelta( seconds = video_info.get( 'duration' ) ) )

					return jsonify({
					'title': title,
					'thumbnail_url': thumbnail_url,
					'author': author,
					'duration': duration
				})

		except Exception as e:

			return Response( str( e ), status = 500 )				

	def _get_video( url ):
		proxies = APIHandler._get_proxies( )

		print( '> Fetching video object' )
		yt = YouTube( url = url, proxies = proxies )		
		print( '< Fetching video object.. done!' )		

		return yt

	def _get_proxies( ):
		print( '> Fetching proxies' )

		if not APIHandler.__proxies_lock:
			APIHandler.__proxies_lock = threading.Lock( )

		if APIHandler.__proxies:
			print( '< Fetching proxies.. done (found in cache)!')			
			return APIHandler.__proxies

		else:
			with APIHandler.__proxies_lock:

				if APIHandler.__proxies:
					print( '< Fetching proxies.. done (found in cache)!')					
					return APIHandler.__proxies

				else:
					proxy = FreeProxy( ).get( )
					if( proxy == '' or proxy == 'There are no working proxies at this time.' ):
						proxy = FreeProxy( timeout = 1 ).get( )

					proxies = { 
						'http': proxy
					}
					print( proxies )

					APIHandler.__proxies = proxies					

					print( '< Fetching proxies.. done!' )					

					return proxies
