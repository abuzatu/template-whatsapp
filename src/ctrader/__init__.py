"""Module to place a trade in CTrader, using the FIX protocol.

Starting with the code of this Brazilian project, that was updated even 2 weeks ago.
https://github.com/ejtraderLabs/ejtraderCT/tree/master/ejtraderCT/api

It has implemented already a FIX protocol from scratch, 
and has built all the sorts of actions needed.

But some things it has removed (modify trades) - to add back.

Some things are only for FOREX, I should add particularities for more assets.

In buy limit and stop there are no TP and SL, they needed to be added.

To try out if we can use different connection for different signals to go to different
accounts. 

So I add the code here to modify it easily, 
later I can contribute to them with the improvements.
"""
