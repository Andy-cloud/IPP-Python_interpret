<?php

require_once "test_src/HtmlGenerator.php";

$dir_for_search = './';
$recursive = False;
$parser = "./parse.php";
$interpret = "./interpret.py";
$parse_only = False;
$int_only = False;
$noclean = False;

$xml_options_file = "/pub/courses/ipp/jexamxml/options";
$jexamxml_path = "/pub/courses/ipp/jexamxml/jexamxml.jar";

function print_help(){
	echo "\t--help\t\t\t výpis nápovědy\n";
	echo "\t--directory=<path>\t složka s testy. Default=aktuální složka\n";
	echo "\t--recursive\t\t testy bude hledat nejen v zadaném adresáři, ale i rekurzivně ve všech jeho
	podadresářích\n";
	echo "\t--parse-script=<file>\t soubor se skriptem v PHP 8.1 pro analýzu zdrojového kódu v IPPcode22. Default=parse.php\n";
	echo "\t--int-script=<file>\t soubor se skriptem v Python 3.8 pro interpret XML reprezentace kódu
	v IPPcode22. Default=interpret.py\n";
	echo "\t--parse-only\t\t testuje pouze parser, nesmí být v kombinaci s --int-script a --int-only\n";
	echo "\t--int-only\t\t testuje pouze interpret, nesmí být v kombinaci s --parse-script a --parse-only\n";
}

function parse_arguments(){
	global $argv, $dir_for_search, $parser, $recursive, $srcFiles, $parse_only, $int_only;

	foreach ($argv as $key => $arg) {
		if(preg_match("/--help/", $arg, $array)){
			if(count($argv) > 2){			
				fwrite(STDERR, "Wrong argument! See --help\n");
				exit(1);
			} else {
				print_help();
				exit(0);
			}
		}else if(preg_match("/--directory=(.+)/", $arg, $array)){
			$dir_for_search = $array[1];
		}else if(preg_match("/--recursive/", $arg, $array)){
			$recursive = True;
		}else if(preg_match("/--parse-script=(.+)/", $arg, $array)){
			$parser = $array[1];
		}else if(preg_match("/--int-script=(.+)/", $arg, $array)){
			$interpret = $array[1];
		}else if(preg_match("/--parse-only/", $arg, $array)){			
			$parse_only = TRUE;
		}else if(preg_match("/--int-only/", $arg, $array)){
			$int_only = TRUE;
		}
	}

	if(($parse_only && $int_only) || ($parse_only && $interpret != "./interpret.py") || ($int_only && $parser != "./parse.php")){
		fwrite(STDERR, "Wrong argument! See --help\n");
		exit(1);
	}

	if($recursive){
		$srcFiles = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir_for_search), RecursiveIteratorIterator::SELF_FIRST);
	} else{
		$srcFiles = new DirectoryIterator($dir_for_search);
	}
}

/**
 * Delete temporary files if exists that has been created during test
 *
 * @param String $your_out_file path to user's interpret out file
 * @param String $temp_xml_file path to xml file that generated user's parser
 * @param String $log_file path to log file that creates jexamxml
 */ 
function delete_temp_files($your_out_file, $temp_xml_file, $log_file){

	unlink($your_out_file);		
	if(file_exists("./delta.xml"))
		unlink("./delta.xml");	

	if(file_exists($temp_xml_file))
		unlink($temp_xml_file);	
	
	// Delete .out.log files if jexamlxml creates them
	if(file_exists($log_file)){	
		unlink($log_file);
	}
}

/**
 * Create rc file if not exists
 *
 * @param String $ref_rc_file path to where sould be refference rc file
 */ 
function create_rc_file_if_not_exists($ref_rc_file){
	if(!file_exists($ref_rc_file)){	
		$file = fopen($ref_rc_file, 'w+');
	    fwrite($file, "0");
	    fclose($file);
	}	
}

/**
 * Create out file if not exists
 *
 * @param String $ref_out_file path to where sould be refference out file
 */ 
function create_out_file_if_not_exists($ref_out_file){
	if(!file_exists($ref_out_file)){	
		$file = fopen($ref_out_file, 'w+');
	    fwrite($file, "");
	    fclose($file);
	}	
}

/**
 * Create in file if not exists
 *
 * @param String $ref_in_file path to where sould be refference in file
 */ 
function create_in_file_if_not_exists($in_file){
	if(!file_exists($in_file)){	
		$file = fopen($in_file, 'w+');
	    fwrite($file, "");
	    fclose($file);
	}	
}

/**
 * Chceck if file is empty
 *
 * @param String $file path to file to check
 * @return True if file exists
 */ 
function is_file_empty($file){

	return !file_get_contents($file);
}

//main
parse_arguments();

HtmlGenerator::print_start_code();

global $argv, $srcFiles, $dir_for_search, $parser, $jexamxml_path, $xml_options_file, $recursive, $parser, $interpret, $parse_only, $int_only, $noclean;

$parent_test_dir = $dir_for_search;
$prev_short_dir = "";
$all_test_count = 0;
$passed_tests = 0;

foreach($srcFiles as $srcFile){
	$out = "";
	$src_path = $srcFile->getPathname();

	if($srcFile->getExtension() == "src"){	
		$all_test_count += 1;

		$fileWithoutExension = dirname($src_path)."/".basename($srcFile->getFilename(), ".".$srcFile->getExtension());

		// Print test directory only if dir has changed
		$short_path = substr($srcFile, strlen($parent_test_dir));		
		$short_dir = basename($parent_test_dir)."/".substr(dirname($src_path), strlen($parent_test_dir));
		if($prev_short_dir !== $short_dir )
			HtmlGenerator::print_path($short_dir);
		$prev_short_dir = $short_dir;

		$ref_rc_file = $fileWithoutExension.".rc";
		$ref_out_file = $fileWithoutExension.".out";
		$in_file = $fileWithoutExension.".in";
		$your_out_file = $fileWithoutExension.".your_out";
		$temp_xml_file = $fileWithoutExension.".temp_xml";		

		create_rc_file_if_not_exists($ref_rc_file);
		create_out_file_if_not_exists($ref_out_file);
		create_in_file_if_not_exists($in_file);	

		$expected_rc = intval(explode(' ',trim(file_get_contents($ref_rc_file)))[0]);

		$parser_rc_is_correct = $parser_out_is_correct = $interpret_rc_is_correct = $interpret_out_is_correct = FALSE;

		if($parse_only){
			exec("php8.1 $parser < \"$src_path\" > \"$your_out_file\"", $trash, $your_parser_rc);		
			exec("java -jar \"$jexamxml_path\" \"$ref_out_file\" \"$your_out_file\" delta.xml /D \"$xml_options_file\"", $trash, $jexamxmlRc);			
	
			if($expected_rc != 0){
				if(is_file_empty($ref_out_file) && is_file_empty($your_out_file))
					$parser_out_is_correct = TRUE;
			}
			else{				
				$parser_out_is_correct = $jexamxmlRc == 0;
			}
			
			$parser_rc_is_correct = $your_parser_rc == $expected_rc;
			$test_passed = $parser_rc_is_correct && $parser_out_is_correct;

			HtmlGenerator::print_test_name($srcFile->getFilename());
			HtmlGenerator::print_test_results($expected_rc, $your_parser_rc, $parser_out_is_correct);
			HtmlGenerator::print_test_results(NULL, NULL, NULL);					
		} else if($int_only){				
			exec("python3.8 $interpret --source=\"$src_path\" < \"$in_file\" > \"$your_out_file\"", $trash, $your_interpret_rc);
			exec("diff \"$ref_out_file\" \"$your_out_file\"", $trash, $diff_out_files_rc);

			$interpret_rc_is_correct = $your_interpret_rc == $expected_rc;
			$interpret_out_is_correct = $diff_out_files_rc == 0;	

			$test_passed = $interpret_rc_is_correct && $interpret_out_is_correct;

			HtmlGenerator::print_test_name($srcFile->getFilename());
			HtmlGenerator::print_test_results(NULL, NULL, NULL);	
			HtmlGenerator::print_test_results($expected_rc, $your_interpret_rc, $interpret_out_is_correct);
		} else{
			// Both
			exec("php8.1 $parser < \"$src_path\" > \"$temp_xml_file\"", $trash, $your_parser_rc);		
			exec("python3.8 $interpret --source=\"$temp_xml_file\" < \"$in_file\" > \"$your_out_file\"", $trash, $your_interpret_rc);
			exec("diff \"$ref_out_file\" \"$your_out_file\"", $trash, $diff_out_files_rc);
	
			$interpret_rc_is_correct = $your_interpret_rc == $expected_rc;
			$interpret_out_is_correct = $diff_out_files_rc == 0;				

			$test_passed = $your_parser_rc == 0 && $interpret_rc_is_correct && $interpret_out_is_correct;

			HtmlGenerator::print_test_name($srcFile->getFilename());
			HtmlGenerator::print_test_results(NULL, $your_parser_rc, NULL);
			HtmlGenerator::print_test_results($expected_rc, $your_interpret_rc, $interpret_out_is_correct);
		}

		if($test_passed){
			HtmlGenerator::print_overall_tick();
			$passed_tests += 1;				
		} else{
			HtmlGenerator::print_overall_x();
		}

		if (!$noclean) {
			delete_temp_files($your_out_file, $temp_xml_file, $ref_out_file.".log");
		}
	}  
}

HtmlGenerator::print_summary($all_test_count, $passed_tests);


?>