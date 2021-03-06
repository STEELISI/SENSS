# -*- coding: utf-8 -*-
#!/usr/bin/python
import time
import glob
import json
import os

#This script is used to read out the matrices from the files and is used to generate the resultant matrix of prediction.
'''
Adapted from example code by Albert Au Yeung (2010)
http://www.quuxlabs.com/blog/2010/09/matrix-factorization-a-simple-tutorial-and-implementation-in-python/#source-code

An implementation of matrix factorization...

@INPUT:
	R     : a matrix to be factorized, dimension N x M
	P     : an initial matrix of dimension N x K
	Q     : an initial matrix of dimension M x K
	K     : the number of latent features
	steps : the maximum number of steps to perform the optimisation
	alpha : the learning rate
	beta  : the regularization parameter
@OUTPUT:
	the final matrices P and Q, steps taken and error

'''
from numpy import array,nonzero,random,dot,percentile,copy,array_equal
from numba import typeof, double, int_
from numba.decorators import autojit, jit

@autojit(locals={'step': int_, 'e': double, 'err': double,'error': double})
def matrix_factorization(R, P, Q, K,steps,desired_sum):
	alpha = 0.0002
	beta = 0.02
	half_beta = beta / 2.0
	N, M = R.shape
	e = 0.0
	step=0
	min_time=99999.0
	error=0
	for step in range(0,steps):
		step=step+1
		for i in xrange(N):
			for j in xrange(M):
				if R[i,j] > 0:
					eij = R[i,j]
					for p in xrange(K):
						eij -= P[i,p] * Q[j,p]
					for k in xrange(K):
						P[i,k] += alpha * (2 * eij * Q[j,k] - beta * P[i,k])
						Q[j,k] += alpha * (2 * eij * P[i,k] - beta * Q[j,k])
		e = 0.0
		for i in xrange(N):
			for j in xrange(M):
				if R[i,j] > 0:
					temp = R[i,j]
					for p in xrange(K):
						temp -= P[i,p] * Q[j,p]
					e = e + temp * temp
					for k in xrange(K):
						e += half_beta * (P[i,k]*P[i,k] + Q[j,k]*Q[j,k])
		error=e/float(desired_sum)*100
		if error<=1:
			break
	return R,P, Q, step, error

def run_recommender(R):
	if len(R)==0:
		return [["0",0,0,0]]
	R=array(R)
	N = len(R)
	M = len(R[0])
	K = 3
	P = random.rand(N,K)
	Q = random.rand(M,K)
	rows, cols = nonzero(R)
	nonzero_R=R[rows,cols]
	desired_sum=0
	for item in nonzero_R:
		desired_sum=desired_sum+(item*item)
	if desired_sum==0:
		return [["0",0,0,0]]
	steps=20000
	start_time=time.time()
	R, P, Q,step,error = matrix_factorization(R, P, Q, K,steps,desired_sum)
	nR = dot(P, Q.T)
	end_time=time.time()
	return [(step,error,end_time-start_time,nR)]


#run_recommender(["192.99.0.0"],"../output_mailinator/2016-06-22","test4")
