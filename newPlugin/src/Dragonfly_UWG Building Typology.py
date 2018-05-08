# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate a default building typology to be used with the "Dragonfly_UWG City" component.  The specific characteristcs of these typologies are based on the US Department of Energy (DoE) Building types.  Wall, roof, and window constructions are based on the climateZone of the epw weather file.
-
Provided by Dragonfly 0.0.02
    Args:
        _bldgGeo: A list of closed breps that represent the geometry of the buildings in the urban area that fall under this typology.
        _bldgProgram: One of the 16 building programs listed from the "Dragonfly_Bldg Programs" component.  The following options are available:
            FullServiceRestaurant
            Hospital
            LargeHotel
            LargeOffice
            MediumOffice
            MidRiseApartment
            OutPatient
            PrimarySchool
            QuickServiceRestaurant
            SecondarySchool
            SmallHotel
            SmallOffice
            StandAloneRetail
            StripMall
            SuperMarket
            Warehouse
        _bldgAge: An integer that sets the age of the buildings represented by this typology.  This is used to determine what constructions make up the walls, roofs, and windows based on international building codes over the last several decades.  Choose from the following options:
            0 = Pre-1980's
            1 = 1980's-Present
            2 = New Construction
        _window2Wall_: A number between 0 and 1 that represents the fraction of the exterior wall surface occupied by windows.  If not value is input here, a default of 0.4 will be used, which is indicative of buildings complying with presceiptive international building codes.
        _roofAlbedo_: A number between 0 and 1 that represents the surface albedo (or reflectivity) of the roof.
        roofVegFract_: A number between 0 and 1 that represents the fraction of the building's roof that is covered in vegetation, such as green roof, grassy lawn, etc.  If no value is input here, it will be assumed that the roof has no vegetation.
        _runIt: Set to "True" to run the component and generate a building typology.
    Returns:
        readMe!: ...
        ------------------: ...
        buildingTypology: A building typology that can be plugged into the "Dragonfly_UWG City" component.
        ------------------: ...
        bldgFootprints: The building geometry as projected onto the world XY plane.  This is used to determine the site coverage ratio and to perform a weighted-average of the building heights.
        facadeBreps: A list of breps representing the exposed facade area of the building breps.  These will be used to calculate the facade-to-site ratio.
"""

ghenv.Component.Name = "Dragonfly_UWG Building Typology"
ghenv.Component.NickName = 'BldgTypology'
ghenv.Component.Message = 'VER 0.0.02\nMAY_08_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
#compatibleDFVersion = VER 0.0.02\nAPR_29_2018
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc

#Dragonfly check.
if not sc.sticky.has_key('dragonfly_release') == True:
    initCheck = False
    print "You should first let Drafgonfly fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Drafgonfly fly...")
else:
    try:
        if not sc.sticky['dragonfly_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['dragonfly_release'].isInputMissing(ghenv.Component): initCheck = False
        df_BuildingTypology = sc.sticky["dragonfly_BuildingTypology"]
    except:
        initCheck = False
        warning = "You need a newer version of Drafgonfly to use this compoent." + \
        "Use updateDrafgonfly component to update userObjects.\n" + \
        "If you have already updated userObjects drag Drafgonfly_Drafgonfly component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

if _runIt == True:
    buildingTypology, bldgFootprints, facadeBreps = df_BuildingTypology.from_geometry(_bldgGeo, 
        _bldgProgram, _bldgAge, _window2Wall_, _roofAlbedo_, roofVegFract_)
    
    print buildingTypology