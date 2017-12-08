<?php

require_once 'vendor/autoload.php';

use PiPHP\GPIO\GPIO;
use PiPHP\GPIO\Pin\PinInterface;

ob_implicit_flush();

function carHighlight($unlocked) {
	
	$gpio_front = new GPIO();
	$gpio_rear = new GPIO();

	$pin_front = $gpio_front->getOutputPin(24);

	$pin_rear = $gpio_rear->getOutputPin(25);

	$pin_front->setValue(PinInterface::VALUE_LOW);
	$pin_rear->setValue(PinInterface::VALUE_LOW);
	
	if ($unlocked == false)
	{
		for($i=0; $i < 4; $i++) {
			usleep(100000);
			$pin_front->setValue(PinInterface::VALUE_HIGH);
			$pin_rear->setValue(PinInterface::VALUE_HIGH);
			usleep(100000);
			$pin_front->setValue(PinInterface::VALUE_LOW);
			$pin_rear->setValue(PinInterface::VALUE_LOW);
		}
	} else {
		for($i=0; $i < 2; $i++) {
			usleep(250000);
			$pin_front->setValue(PinInterface::VALUE_LOW);
			$pin_rear->setValue(PinInterface::VALUE_LOW);
			usleep(250000);
			$pin_front->setValue(PinInterface::VALUE_HIGH);
			$pin_rear->setValue(PinInterface::VALUE_HIGH);
		}
	}
}





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
		carHighlight(true);
		sleep(3);
		// call function for car disco with var $unlock_state
		
	} else if (!$result['need_to_be_open'] && $result['is_open']) {
		$data = array('is_open' => false);
		$unlocked = callApi($url, $vin, $data, 'POST');
		$unlock_state = $unlocked['success'];
		$result = callApi($url, $vin);
		var_dump('locked');
		carHighlight(false);
		sleep(3);
		// call function for car disco with var $unlock_state
		
	} else {
		// if response param need_to_be_open and is_open are same => lock or unlock
		$result = callApi($url, $vin);
		var_dump('waiting');
	}
	
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



