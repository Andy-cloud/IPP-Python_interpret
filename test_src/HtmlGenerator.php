<?php

class HtmlGenerator{
/**
 * Print html code to stdout
 */ 	

public static function print_start_code(){
	echo '<!DOCTYPE html>
<html>
<head>
	<title>Test IPPcode19</title>
	<style>
        table {        
        	margin-top: 25px;
            width: 80%;
            -webkit-box-shadow: 1px 1px 5px 0px rgba(0,0,0,0.47);
            -moz-box-shadow: 1px 1px 5px 0px rgba(0,0,0,0.47);
            box-shadow: 1px 1px 5px 0px rgba(0,0,0,0.47);
            font-family: Helvetica, Arial, sans-serif;
        }        
        table td, table th {
            padding: 5px;
            text-align: center;
        }
        table tr:nth-child(even){background-color: #f2f2f2;}
        table tr{
        	background-color: #fff;
        }
        table th, .collumns {        	
            padding-top: 6px;
            padding-bottom: 6px;
            background-color: #3498DB;
            color: white;
        }
        .main-cols{
        	border-bottom: solid; 
        	border-color: #000; 
        	border-width: 1px;
        }
        .tick-symbol{
        	color: #0d0;
        }
        .x-symbol{
        	color: #d00;
        }  
        .test-path{
            background-color: #50505c !important;  
            color: white;;   
        }    
    </style>
</head>
<body>
	<table rules=groups align="center">
		<colgroup>
    		<col span="1">    		
  		</colgroup>
  		<colgroup>
    		<col span="4">    		
  		</colgroup>
  		<colgroup>
    		<col span="4">    		
  		</colgroup>

		<thead >
			<tr>		
				<th></th>	
				<th class="main-cols" colspan="4">Parser</th>				
				<th class="main-cols" colspan="4">Interpret</th>
				<th></th>	
			</tr>
			<tr >
				<th>Name</th>
				<td class="collumns" >Expected</td>
				<td class="collumns" >Real</td>
				<td class="collumns" >RC</td>
				<td class="collumns" >Out</td>
				<td class="collumns" >Expected</td>
				<td class="collumns" >Real</td>
				<td class="collumns" >RC</td>
				<td class="collumns" >Out</td>
				<th>Overall</th>
			</tr>
		</thead>
		<tbody>'."\n";
}

public static function print_path($path){
	echo '			<tr>
				<td class="test-path">/'.$path.'</td>
				<td colspan="4"></td>
				<td colspan="4"></td>
				<td></td>				
			</tr>'."\n";
}

public static function print_test_name($test_name){
	echo "\t\t\t".'<tr>'."\n\t\t\t\t".'<td>'.$test_name.'</td>'."\n";
}

public static function print_test_results($expected_rc, $real_rc, $result){

	$rc_data_missing = FALSE;

	if(is_null($expected_rc)){
		$expected_rc = "-";
		$rc_data_missing = TRUE;
	}

	if(is_null($real_rc)){
		$real_rc = "-";
		$rc_data_missing = TRUE;
	}

	echo "\t\t\t\t".'<td>'.$expected_rc.'</td>'."\n\t\t\t\t".'<td>'.$real_rc.'</td>'."\n";

	if($rc_data_missing){
		echo "\t\t\t\t".'<td>-</td>'."\n";
	}else{
		if($expected_rc == $real_rc){
			echo "\t\t\t\t".'<td class="tick-symbol">&#10004</td>'."\n";
		} else{
			echo "\t\t\t\t".'<td class="x-symbol">&#10007</td>'."\n";
		}		
	}

	if(is_null($result)){
		echo "\t\t\t\t".'<td>-</td>'."\n";
	}else{
		if($result == TRUE)	{
			echo "\t\t\t\t".'<td class="tick-symbol">&#10004</td>'."\n";
		} else{
			echo "\t\t\t\t".'<td class="x-symbol">&#10007</td>'."\n";
		}	
	}
}

public static function print_overall_tick(){

	echo "\t\t\t".'<td class="tick-symbol">Ok</td>'."\n\t\t\t".'</tr>'."\n";
}

public static function print_overall_x(){

	echo "\t\t\t".'<td class="x-symbol">Fail</td>'."\n\t\t\t".'</tr>'."\n";
}

public static function print_summary($all_tests, $passed_tests){

	echo '			<tr>
				<th colspan="9"></th>				
				<th >'."$passed_tests/$all_tests".'</th>
			</tr>
		</tbody>
	</table>
	</body>
	</html>';	
}

}
?>