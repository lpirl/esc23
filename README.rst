This tool is intended to extend Ardour3 sessions converted from Ardour2.

It's probably very much tailored to my **use case**:
You recorded in Ardour2 but want to edit and mix in Ardour3.

The tested scenario is to apply this script to a session that has been *just* converted to from Ardour2 to Ardour3. In other words:

#. backup your Ardour2 project
#. open your Ardour2 session in Ardour3
#. Ardour3 will convert the session (but leave out a few things)
#. save the Ardour3 session
#. **apply this script** to the just saved session file
#. open the resulting, extended Ardour3 session
#. start working

See ``./esc23.py -h`` for help.

**Contribute:** See ``processors/add_monitor_bus.py`` for a simple example.
Subclasses of ``AbstractBaseProcessor`` in the module ``processors``
will be loaded and executed automagically.
