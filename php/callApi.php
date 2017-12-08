<?php
ob_implicit_flush();

$url = 'https://gr2lqfx86d.execute-api.eu-central-1.amazonaws.com/prod/lockcheck';
$vin_token = '3015def63a839df84029c7a10554a095af1f9d8';
$vin = array('vin_token' => $vin_token);
$result = callApi($url, $vin);


while (true)
{
	// check json response
	//var_dump($result);
	// if response param need_to_be_open and is_open differ => lock or unlock
	if ($result['need_to_be_open'] && !$result['is_open']) {
		$data = array('is_open' => true);
		$unlocked = callApi($url, $vin, $data, 'POST');		
		$unlock_state = $unlocked['success'];
		$result = callApi($url, $vin);
		var_dump('unlocked');
		// call function for car disco with var $unlock_state
		
	} else if (!$result['need_to_be_open'] && $result['is_open']) {
		$data = array('is_open' => false);
		$unlocked = callApi($url, $vin, $data, 'POST');
		$unlock_state = $unlocked['success'];
		$result = callApi($url, $vin);
		var_dump('locked');
		// call function for car disco with var $unlock_state
		
	} else {
		// if response param need_to_be_open and is_open are same => lock or unlock
		$result = callApi($url, $vin);
		var_dump('waiting');
	}
	sleep(3);
}

function callApi($url, $vin, $data = array(), $method = '') {
    $curl = curl_init();
	curl_setopt($curl, CURLOPT_FRESH_CONNECT, 1);
	curl_setopt($curl, CURLOPT_HTTPHEADER, array('Cache-control: no-cache'));
	switch ($method)
	    {
	        case "POST":
				$data = array_merge($data, $vin);
	            curl_setopt($curl, CURLOPT_POST, 1);
				curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
	            break;
		    default:
				curl_setopt($curl, CURLOPT_HTTPGET, 1);
				foreach ($vin as $key => $value) {
					$url = $url.'?'.$key.'='.$value;
				}
		        break;
	    }	

    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);

    $result = curl_exec($curl);
	$result = json_decode($result, true);
	
	curl_close($curl);
	return $result;
	
}

?>

