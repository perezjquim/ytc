from flask import Blueprint, Response, request, send_from_directory
from datetime import datetime
from pytube import YouTube
import os
from moviepy.editor import VideoFileClip
from fp.fp import FreeProxy

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

	@api.route( '/crop-video', methods = [ 'GET' ] )
	def crop_video( ):

		args = request.args

		print( '> Fetching proxy' )
		proxy = FreeProxy( ).get( )
		proxies = { 
			'http': proxy
		}
		print( proxies )
		print( '< Fetching proxy' )

		current_datetime = datetime.now( )
		current_datetime_str = current_datetime.isoformat( )
		video_tmp_directory = './'
		video_ydl_filename = 'tmp-ydl.mp4'
		video_ffmpeg_filename = 'tmp-ff.mp4'		

		video_output_filename = 'YTC - {}.mp4'.format( current_datetime_str )		

		start_datetime = datetime.strptime( args[ 'start_time' ], "%M:%S" )
		start_timedelta = start_datetime - datetime( 1900, 1, 1 )
		start_time_in_seconds = start_timedelta.total_seconds( )

		end_datetime = datetime.strptime( args[ 'end_time' ], "%M:%S" )
		end_timedelta = end_datetime - datetime( 1900, 1, 1 )
		end_time_in_seconds = end_timedelta.total_seconds( )		

		print( '> Downloading' )
		yt = YouTube( url = args[ 'url' ], proxies = proxies )
		yt_stream = yt.streams.get_by_itag( 18 )
		yt_stream.download( filename = video_ydl_filename )
		print( '< Downloading' )

		print( '> Cutting' )
		clip = VideoFileClip( video_ydl_filename ).subclip( start_time_in_seconds, end_time_in_seconds )
		clip.write_videofile( filename = video_ffmpeg_filename, codec = "libx264", temp_audiofile = 'temp-audio.m4a', remove_temp = True, audio_codec = 'aac' )		
		clip.close( )
		os.remove( video_ydl_filename )	
		print( '< Cutting' )		

		print( '> Preparing request' )	
		succ_response = send_from_directory( video_tmp_directory, filename = video_ffmpeg_filename, as_attachment = True  )
		succ_response.headers[ 'Content-Disposition' ] = "attachment; filename={};".format( video_output_filename )
		succ_response.headers[ 'Access-Control-Expose-Headers' ] = 'Content-Disposition'
		print( '< Preparing request' )		

		print( '!! DONE !!' )	

		return succ_response
		