﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WallArea : Area {

    public GameObject wall;
    public GameObject academy;
    public GameObject block;
    public GameObject goalHolder;

	// Use this for initialization
	void Start () {
		academy = GameObject.Find("Academy");
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    public override void ResetArea() {
		int wallHeightMin = (int)academy.GetComponent<WallAcademy>().minWallHeight;
		int wallHeightMax = (int)academy.GetComponent<WallAcademy>().maxWallHeight;
		wall.transform.localScale = new Vector3(12f, Random.Range(wallHeightMin, wallHeightMax), 1f);
        block.transform.position = new Vector3(Random.Range(-3.5f, 3.5f), 1f, Random.Range(-4f, -8f)) + gameObject.transform.position;
		goalHolder.transform.position = new Vector3(Random.Range(-3.5f, 3.5f), 0.25f, 0f) + gameObject.transform.position;
	}
}
