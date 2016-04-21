var helper;
var helperLocalize = "<h3>Localize</h3> Localize shows the anycast instances of the target"
var helperAllAnycast = "<h3>All Anycast</h3> All Anycast shows all the anycast instances for all the target"
var helperTarget = "<h3>Target</h3> Field for the input target, it is possible search by name or by IP. An autocomplete function provides suggestions while you type into the field."

var helperPublicInfo = "<h3>Target with public info</h3> List of targets provide a public list with the deployed instances"
var helperGroundTruth = "<h3>Target with ground truth</h3> List of targets provide a public list with the deployed instances and for each probes we know wich instance is contacted"
var helperVisualization="<h3>Visualization</h3>It shows different level of detail.<h3>Basic visualization</h3> This visualization shows the anycast replicas"+
                        "<h3>Extended visualization</h3> In addition to the basic visualization this one shows also the vantage points and circles"+
                        "<h3>Everything visualization</h3> This visualization shows all the information available"

var helperToggle="<h3>Toogle</h3><h3>Ground truth</h3>This option shows the targets contacted by the vantage points"+
                "<h3>Replicas</h3>This option shows the replicas discovered"+
                "<h3>Vantage Points</h3>This option shows the probes used for the measurement"+
                "<h3>Circles</h3>This option shows the circles rapresenting a measure of the delay"


var helperToggleOld="<h3>Toogle</h3><h3>Ground truth</h3>This option shows the targets contacted by the vantage points"+
                "<h3>Replicas</h3>This option shows the replicas discovered"+
                "<h3>Misses instances</h3>This option shows the instances published but not contacted by the probes"+
                "<h3>False positive</h3>This option shows the false positive discovered thanks to the ground truth"+
                "<h3>Probes</h3>This option shows the probes used for the measurement"+
                "<h3>Circles</h3>This option shows the circles rapresenting a measure of the delay"
function showHelper(element) {
    helper = document.getElementById('helperMode');
    if (helper.checked) {
        if (element === "localize") {
            return helperLocalize
        } else if (element === "allAnycast") {
            return helperAllAnycast
        } else if (element === "targetInput") {
            return helperTarget
        } else if (element === "publicInfo") {
            return helperPublicInfo
        } else if (element === "groundTruth") {
            return helperGroundTruth
        } else if (element === "basic") {
            return helperBasic
        } else if (element === "extended") {
            return helperExtended
        } else if (element === "everything") {
            return helperEverything
        } else if (element === "custom") {
            return helperCustom
        } else if (element === "GT") {
            return helperGT
        } else if (element === "hit") {
            return helperHit
        } else if (element === "miss") {
            return helperMiss
        } else if (element === "FP") {
            return helperFP
        } else if (element === "probes") {
            return helperProbes
        } else if (element === "circles") {
            return helperCircles
        }else if (element === "visualization") {
            return helperVisualization
        }else if (element === "toggle") {
            return helperToggle
        }
    }
}
