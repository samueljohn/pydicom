# fixer.py
"""Code to fix non-standard dicom issues in files
"""
# Copyright (c) 2008-2014 Darcy Mason
# This file is part of pydicom, released under a modified MIT license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/darcymason/pydicom

from pydicom import config
from pydicom import datadict

def fix_separator_callback(raw_elem, **kwargs):
    """Used by fix_separator as the callback function from read_dataset
    """
    return_val = raw_elem
    try_replace = False
    
    # If elements are implicit VR, attempt to determine the VR
    if raw_elem.VR is None:
        try:
            VR = datadict.dictionaryVR(raw_elem.tag)
        # Not in the dictionary, process if flag says to do so
        except KeyError:
            try_replace = kwargs['process_unkown_VR']
        else:
            try_replace = VR in kwargs['for_VRs']
    else:
        try_replace = raw_elem.VR in kwargs['for_VRs']
    
    if try_replace:
        # Note value has not been decoded yet when this function called,
        #    so need to replace backslash as bytes
        new_value = raw_elem.value.replace(kwargs['invalid_separator'], b"\\")
        return_val = raw_elem._replace(value=new_value)

    return return_val
    

def fix_separator(invalid_separator, for_VRs=["DS", "IS"],
                  process_unknown_VRs=True):
    """A callback function to fix RawDataElement values using 
    some other separator than the dicom standard backslash character
    
    Parameters
    ----------
    invalid_separator : bytes
        A single byte to replace with dicom backslash, in raw data element
        values before they have been decoded or processed by pydicom
    for_VRs : list, optional
        A list of VRs for which the replacement will be done.
        If the VR is unknown (for example, if a private element),
        then process_unknown_VR is used to determine whether to replace or not.
    process_unknown_VRs: boolean, optional 
        If True (default) then attempt the fix even if the VR is not known.
    
    Returns
    -------
    No return value.  However, the callback function will return either
    the original RawDataElement instance, or a fixed one.
    """
    config.data_element_callback = fix_separator_callback
    config.data_element_callback_kwargs = {
        'invalid_separator': invalid_separator,
        'for_VRs': for_VRs
        }
    