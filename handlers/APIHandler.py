from flask import Blueprint, Response, request, send_from_directory
from datetime import datetime
import youtube_dl #dummy
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

	@api.route( '/crop-video', methods = [ 'GET' ] )
	def crop_video( ):
		args = request.args

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
		with youtube_dl.YoutubeDL( { "format": "18", "outtmpl": video_ydl_filename } ) as ydl:
        		ydl.download( [ args[ 'url' ] ] )		
		print( '< Downloading' )

		print( '> Cutting' )
		ffmpeg_extract_subclip( video_ydl_filename, start_time_in_seconds, end_time_in_seconds, targetname = video_ffmpeg_filename )	
		os.remove( video_ydl_filename )		
		print( '< Cutting' )		

		print( '> Preparing request' )	
		succ_response = send_from_directory( video_tmp_directory, filename = video_ffmpeg_filename, as_attachment = True  )
		succ_response.headers[ 'Content-Disposition' ] = "attachment; filename={};".format( video_output_filename )
		succ_response.headers[ 'Access-Control-Expose-Headers' ] = 'Content-Disposition'
		print( '< Preparing request' )			

		return succ_response