// ----------------------------------------
// Add / Remove Input Text Field
// ----------------------------------------

// Add input field for multi sources feed : RSSFeed, FacebookFeed etc.
$("button.add-input").click(function(event){
    event.preventDefault();
    var inputs = $(this).siblings('div.col-sm-6');
    var numInputs = inputs.length;
    if( numInputs > 0){
        var newInput = $(inputs[0]).clone();
        newInput.addClass("col-sm-offset-2").css("margin-top", "10px");
        newInput.insertAfter( $(inputs[numInputs-1]) );
    }
});

// Remove input field for multi sources feed : RSSFeed, FacebookFeed etc.
$("button.remove-input").click(function(event){
    event.preventDefault();
    var inputs = $(this).siblings('div.col-sm-6');
    var numInputs = inputs.length;
    if( numInputs > 1){
        $(inputs[numInputs-1]).remove();
    }
});

// ----------------------------------------
// Enable Bootstrap Tooltip
// ----------------------------------------
    
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
});

// ----------------------------------------
// Save and Choose Clock Settings
// ----------------------------------------
    
$("#chooseClock").click(function(event){
    // Two ways to specify the clock settings
    //   -- 1. By start time, end time and duration
    //   -- 2. By start time and acceleration factor
    event.preventDefault();
    $('#chooseClockSettingsModal').modal('hide');
    if( $('input[name="clockOption"]:checked').val() === "datetime" ){
        $('#clockTimeSettingsModal').modal();
    } else {
        $('#acceleratorSettingsModal').modal();
    }
});

$("button[name='saveClockSettings']").click(function(event){
    event.preventDefault();

    $modal = $(this).closest('div.modal');
    
    // Get Form Data
    var form_data = new FormData();
    
    $modal.find('form').serializeArray().reduce(function(obj, item) {
        form_data.append( item.name, item.value );
    }, {});
    
    console.log(form_data);
    
    // Send request
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/save-clock-settings", true);
    xhr.onreadystatechange = (event) => {
      if (xhr.readyState == XMLHttpRequest.DONE) {
          $modal.modal('hide');
          $('#confirmSaveSettingsModal').modal();
      }
    }
    xhr.send(form_data);
});

// ----------------------------------------
// Drag, drop and link
// ----------------------------------------

// Configuration for jsPlumb
jsPlumb.importDefaults({
    Endpoint: ["Dot", {radius: 3}],
    Connector:"Flowchart",
    HoverPaintStyle: {stroke: "#1e8151", strokeWidth: 2 },
    ConnectionOverlays: [
        [ "Arrow", {
            location: 1,
            id: "arrow",
            visible: true,
            length: 14,
            foldback: 0.8
        } ]
    ]
});

// Make draggable using jQuery-ui
// The component with .disable class is not supported for the moment
// To disable them, we will not make it able for dragging
$('#selector li:not(.disable)').draggable({
    containment: ".droppable",
    revert: 'invalid',
    cursor: 'move',
    appendTo: "#workflow",
    helper: function() {
        var $this = $(this).clone();
        var $img = $this.find('img');
        var text = $('<p></p>').text( $.trim( $this.text()) ).addClass('text-center');
        var anchor = $('<div></div>').addClass('anchor');
        var component = $('<div></div>').addClass('component').attr('type', $this.attr('name'));
        return component.append($img).append(text).append(anchor);
    }
});

// Make dropppable using jQuery-ui
$('#panel').droppable( {
    drop: function(event, ui){
        // Find the location where to drop the component
        var left = ui.offset.left - $(this).offset().left;
        var top = ui.offset.top - $(this).offset().top;
        var $component = $(ui.helper).clone(false).css('left', left).css('top', top);
        // For components that doesn't require settings
        // Add class .saved -> the border will be green
        var type = $component.attr("type");
        if( type == "RawStream" || type == "Stream" || type == "Scouter"){
            $component.addClass("saved");
        }
        // Append to workflow space
        $('#panel').append($component);
        // Init node with jsPlumb
        initCmpt($component);
        addCmpt($component);
    }
});
    
// Init component
function initCmpt($node){
    // Make the dropped component draggable
    jsPlumb.draggable( $node, { 
        containment: true,
        // Every time move the component
        // Update the saved location at backend
        stop: function(e){
            var id = $(e.el).attr('id');
            var ui_left = e.pos[0];
            var ui_top = e.pos[1];
            updateCmptLoc(id, ui_left, ui_top);
        }
    });
    // Make it able to be drraged from anchor (ornage point)
    jsPlumb.makeSource( $node, {
        filter: ".anchor",
        anchor: "Continuous"
    });
    // Make it able to be dragged link to
    jsPlumb.makeTarget( $node, {
        anchor: "Continuous",
        allowLoopback: false
    }); 
}

// ----------------------------------------
// Add Component & Link in Back-End
// ----------------------------------------

// Save the newly dropped component information at back-end
function addCmpt($component){
    
    // Obtain component information
    var cmptType = $component.attr('type');
    var id = $component.attr('id');
    var ui_left = $component.attr('left');
    var ui_top = $component.attr('top');
    
    // Append these information -> form data
    var data = new FormData();
    data.append('cmptType', cmptType);
    data.append('id', id);
    data.append('ui_left', ui_left);
    data.append('ui_top', ui_top);
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/add-component", true);
    xhr.send(data);
}

// Save new link in back-end
function addLink(srcCmptId, trgCmptId){
    // Save source component and target component ids
    var data = new FormData();
    data.append('srcCmptId', srcCmptId);
    data.append('trgCmptId', trgCmptId);
    // Send to server to save these informations
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/add-link", true);
    xhr.send(data); 
}

// ----------------------------------------
// Import Default Workflow
// ----------------------------------------
    
$("button#import_workflow").click(function(event) {
    
    // Clear workflow space before importing
    $("#panel div.component").each(function(){
        
        // Remove all components and links in the front-end
        var id = $(this).attr('id');
        jsPlumb.remove(id);
        
        // Update the components and links information in back-end
        // To clear the current workflow information
        delCmpt(id);
        delConns(id);
    });
    
    var xhr = new XMLHttpRequest();
    var default_workflow = [];
    xhr.open("POST", "/create-project/default-workflow", true);
    xhr.onreadystatechange = (event) => {
      if (xhr.readyState == XMLHttpRequest.DONE) {
          // Load default workflow json from back-end
          default_workflow = JSON.parse( xhr.responseText );
          addDefaultCmpt(default_workflow);
          addDefaultLink(default_workflow);
      }
    }
    xhr.send();
});

function addDefaultCmpt(default_workflow){
    // Add components to workflow space
    for(var i = 0; i < default_workflow.length ; i++ ){
        // New node
        var node = $(`
            <div class="component ui-draggable-dragging jsplumb-draggable jsplumb-droppable" style="position: absolute;">
                <img>
                <p class="text-center"></p>
                <div class="anchor"></div>
            </div>`
        );
        // Add positional information for dropped component
        var cmpt = default_workflow[i];
        node.css('top', cmpt['top']).css('left', cmpt['left']);
        node.attr('type', cmpt['type']);
        node.attr('id', cmpt['id']);
        node.find('img').attr('src', cmpt['img_src']);
        node.find('p').text(cmpt['p_text']);
        // For these components that do not need the configuration
        // Add saved class for it
        if( ["RawStream", "Stream", "Scouter"].includes(cmpt['type']) ){
            node.addClass("saved");
        }
        // Append and init node 
        $("#panel").append(node);
        // Make drag, drop and connect
        initCmpt(node);
        // Add component information at back-end
        addCmpt(node);
    }
}
    
function addDefaultLink(default_workflow) {
    // Connect default workflow components
    for(var i = 0; i < default_workflow.length ; i++ ){
        var src_cmpt = default_workflow[i];
        for(var j = 0; j < src_cmpt['linksTo'].length ; j++ ){
            var src_cmpt_id = src_cmpt['id'];
            var trg_cmpt_id = src_cmpt['linksTo'][j];
            jsPlumb.connect({
                source: src_cmpt_id,
                target: trg_cmpt_id
            });
        }
    }  
}

// ----------------------------------------
// Update Workflow Information
// ----------------------------------------
    
function updateCmptLoc(id, ui_left, ui_top){
    // Update Location when Moving the Component's location
    var data = new FormData();
    data.append('id', id);
    data.append('ui_left', ui_left);
    data.append('ui_top', ui_top);
    
    // Update server side's saving state
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/update-component-location", true);
    xhr.send(data);
}

// ----------------------------------------
// Set Window Span
// ----------------------------------------

// Update workflow connection
jsPlumb.bind("connection", function(conn, event) {    
    
    var srcCmptId = conn.sourceId;
    var trgCmptId = conn.targetId;
    
    // Check if the new connection is duplicated
    dupl_conns = jsPlumb.getConnections({
        source: srcCmptId,
        target: trgCmptId
    });
    
    if( dupl_conns.length > 1 ){
        // Detach if duplicate connections
        jsPlumb.detach(dupl_conns[1]);
    } else {
        
        var srcType = $(conn.source).attr('type');
        var trgType = $(conn.target).attr('type');
        
        // Check if connection is legal or not
        if( isLegalConn(srcType, trgType) ){
            addLink(srcCmptId, trgCmptId);  
            // Window Span is a configuration of connection link between Stream and Filter
            if(  srcType === "Stream" && trgType === "Filter" ){
                $('#windowSettingsModal').modal();  
                $('#windowSettingsModal').on("click", "button[name='saveWindowSpan']", function(event){
                    $('#windowSettingsModal').modal('hide');
                    // Get window span
                    var windowSpan = $('input[name="windowSpan"]').val();
                    var data = new FormData();
                    data.append("srcCmptId", srcCmptId);
                    data.append("trgCmptId", trgCmptId);
                    data.append("windowSpan", windowSpan);
                    // Save the window span in server side
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", "/create-project/save-link-settings", true);
                    xhr.send(data);
                });
            } 
        } else {
            // Detach if illegal connection
            jsPlumb.detach(conn);
            // Suggest user the legal connections
            legalTargetTypes = getLegalTargets(srcType);
            bootbox.alert("Alert: This component could only connect to: " + legalTargetTypes.join(", "));
        }
    }
});

// ----------------------------------------
// Check Legal Connections
// ----------------------------------------

// Legal connections: source -> target
legalConns = {
    "RawSource":    ["RawStream"],
    "RawStream":    ["Sampler", "Cleaner", "Converter"],
    "Source":       ["Stream"],
    "Stream":       ["Filter", "Sink", "Strider"],
    "RdfFeed":      ["Filter"],
    "RdfStore":     ["Filter"],
    "SparqlFeed":   ["Filter"],
    "Sink":         ["AnomalyDetection", "RdfStore"],
    "Sampler":      ["RawStream"],
    "Cleaner":      ["RawStream"],
    "Converter":    ["Stream"],
    "Filter":       ["Stream"],
    "AnomalyDetection": ["Stream", "RdfStore"],
    "Scouter":      ["Stream"],
    "RSSFeed":      ["Scouter"],
    "FacebookFeed": ["Scouter"],
    "TwitterFeed":  ["Scouter"],
    "OpenDataFeed": ["Scouter"],
}
    
function isLegalConn(srcType, trgType) {
    // Check if the link between srcType and trgType is legal
    return legalConns[srcType].includes(trgType);
}

function getLegalTargets(srcType){
    // Get the legal connections target for source type
    return legalConns[srcType];
}

// ----------------------------------------
// Get component settings
// ----------------------------------------

// Click component in workflow space to show corresponding settings panel
// Load this component settings if already saved in server
$('#panel').on('click', '.component', function(e) {
    
    e.preventDefault();
    
    // Add border for clicked component
    // Selected component will be surrounded by draken orange border
    $('#panel .component').removeClass('selected');
    $(this).addClass('selected');
    
    // Show corresponding form by component type
    // i.e.
    //    RawStream -> type = RawStreamSettings
    //    Filter    -> type = FilterSettings
    type = $(this).attr('type') + 'Settings';
    $form = $('#cmpt_settings form[type="' + type + '"]');
    
    // Set the form attr cmpt_id as the component id
    cmpt_id = $(this).attr('id');
    $form.attr('cmpt_id', cmpt_id);
    
    // Empty all form controls value
    $form[0].reset();
    
    // Load settings value from server
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/get-component-settings", true);
    
    xhr.onreadystatechange = (event) => {
      if (xhr.readyState == XMLHttpRequest.DONE) {
          // Set form control value with response
          json = JSON.parse(xhr.responseText);
          console.log(json);
          for (var name in json) {
            // This json object has:
            //   key : is the name of input or textarea
            //   value : is the value of this input or textarea
            if (json.hasOwnProperty(name)) {
                // Get input or textarea
                $input = $form.find('input[name="'+name+'"]');
                $textarea = $form.find('textarea[name="'+name+'"]');
                $select = $form.find('select[name="'+name+'"]');
                // Set value for them
                if( $input.attr('type') == 'radio' ){
                    // If it is radio box, make the corresponding radio button checked
                    $input.each(function(){
                        if( $(this).val() == json[name]){
                            $(this).prop('checked', true);
                        }
                    });
                } else if( $input.attr('type') == 'file' ){
                    // do nothing
                    // Can not set value if input type is 'file'
                } else {
                    $form.find('input[name="'+name+'"]').val(json[name]);
                    $form.find('textarea[name="'+name+'"]').val(json[name]);   
                }
                $select.val(json[name]);
            }
            // Deal with multiple inputs
            if( name == "locations" || name == "pages" || name == "hashTags" ){
                $inputs = $form.find('input[name="'+name+'"]');
                values = json[name].split(" || ");
                for (var i = 0; i < $inputs.length; i++) {
                    $($input[i]).val(values[i]);
                }
            }
          }
          // Hide others forms but only show this form
          $form.siblings().addClass('hide');
          $form.removeClass('hide');
      }
    }
    
    data = new FormData();
    data.append('id', cmpt_id);
    
    xhr.send(data);
});

// ----------------------------------------
// Save component settings
// ----------------------------------------

// Click button to save component settings at server side
$('button[name="saveCmptSettings"]').click(function(e){
    
    e.preventDefault();
    
    // Get nearest form
    $form = $(this).closest('form');
    
    // Iterate form control to get name -> value mapping
    map = {};
    
    $form.find('input, textarea').each(function(){
        if( $(this).attr('type') === 'radio' ){
            // For radio input, only record the checked option
            if( $(this).is(':checked') ){
                map[ $(this).attr('name') ] = $(this).val();
            }
        } else if( $(this).attr('type') === 'file' ){
            map[ $(this).attr('name') ] = $(this).val();
        } else {
            map[ $(this).attr('name') ] = $(this).val();
        }
    });

    $form.find('select').each(function(){
        map[$(this).attr('name')] = $(this).val();
    });
    
    // Process locations, pages & tags multi inputs fields
    // Join multiple values using ' || ' as delimiter
    if( $form.find("input[name='locations']").length > 0 ){
        var locations = [];
        $form.find("input[name='locations']").each(function(){
            locations.push($(this).val());
        });
        map['locations'] = locations.join(' || ');   
    }
    
    if( $form.find("input[name='pages']").length > 0 ){
        var pages = [];
        $form.find("input[name='pages']").each(function(){
            pages.push($(this).val());
        });
        map['pages'] = pages.join(' || ');                                        
    }
    
    if( $form.find("input[name='hashTags']").length > 0 ){
        var hashTags = [];
        $form.find("input[name='hashTags']").each(function(){
            hashTags.push($(this).val());
        });
        map['hashTags'] = hashTags.join(' || ');                                        
    }
    
    console.log(map);
    
    var data = new FormData();
    var cmpt_id = $form.attr('cmpt_id');
    data.append('cmpt_id', cmpt_id);
    // Split to get cmpt_type : "FilterSettings" -> "Filter"
    var cmpt_type = $form.attr('type').split("Settings")[0];
    data.append('cmpt_type', cmpt_type);
    for ( var key in map ) {
        data.append(key, map[key]);
    }
    
    // Save settings value to server
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/save-component-settings", true);
    xhr.onreadystatechange = (event) => {
      if (xhr.readyState == XMLHttpRequest.DONE) {
          $("#"+cmpt_id).addClass("saved");
      }
    }
    xhr.send(data);
});

// ----------------------------------------
// Handle Special Configuration Settings
// (open more configuration to some specifics
// parameters)
// ----------------------------------------

// Raw Source Read Step Settings
//
// If user choose the use real time data
//   - He needs to set the readStep parameter
//   - In the UI level, we will show up this form input group for settings
//
// Else if user doesn't choose the real time data, i.e. it
//   use the data from files
//   - He will not need to set stepRead parameter
//   - In the UI level, we will also remove the input field

$("form[type='RawSourceSettings'] input[name='realTimeData']").on("change", function(){

    console.log("Change use or not real time data settings");

    // If user choose to use real time data
    if( $(this).val() == "True" ){
        // Create a read step input field
        var $readStepInput = $(`
          <div class="form-group">
            <label class="control-label col-sm-2" for="readStep">Read Step :</label>
            <div class="col-sm-6">
                <input type="text" class="form-control" name="readStep" placeholder="PT15M" value="PT15M">
                <small class="text-muted">Reading Step </small>
            </div>
          </div>
        `);
        // Append the read step input field after selection
        $readStepInput.insertAfter($(this).closest(".form-group"));
    } else {
        // If user choose not to use the real time data
        // Hide the form input for read step
        
        // Get the raw source settings form
        var $form = $(this).closest("form");
        // Iterate each form group of the raw source settings form
        $form.children(".form-group").each(function(){
            console.log($(this).find("input[name='readStep']").length);
            // If it's the form input group for read step 
            if( $(this).find("input[name='readStep']").length != 0 ){
                // Remove it
                $(this).remove();
            }
        });
    }
});

// Sink Settings
//
// When user choose different sink type, we will show different input fields
// There are two kinds of sink type:
//   - File sink
//   - Triple store sink
//
// For File sink, need to show two input fields for setting the configuration
//   - outputFile
//   - outputFormat
// For triple store sink, don't need to give any configuration, just need to
//   connect to a triple store
//
$("form[type='SinkSettings'] input[name='sinkType']").on("change", function(){

    console.log("Change the choice of sink settings type");

    // If user choose to sink to file
    if( $(this).val() == "File" ){
        // Insert some form inputs for file outputs
        var $fileSinkInputs = $(`
          <div class="form-group">
            <label class="control-label col-sm-2" for="outputFile">Output File Name :</label>
            <div class="col-sm-6">
                <input class="form-control" name="outputFile" type="text" placeholder="stdout" value="stdout">
                <small class="text-muted">Name of Output file.</small>
            </div>
          </div>
          <div class="form-group">
            <label class="control-label col-sm-2" for="outputFormat">Output Format :</label>
            <div class="col-sm-6">
                <input class="form-control" name="outputFormat" type="text" placeholder="Turtle" value="Turtle">
                <small class="text-muted">Specify the output Format</small>
            </div>
          </div>
        `);
        // Append the input fields after selection
        $fileSinkInputs.insertAfter($(this).closest(".form-group"));
    } else {
        // If user choose to sink to Triple Store
        // Hide the form input for file output settings
        var $form = $(this).closest("form");
        // Iterate each form group of the sink settings form
        $form.children(".form-group").each(function(){
            console.log($(this).find("input[name='outputFile']").length);
            // If it's the form input group for output file settings
            if( $(this).find("input[name='outputFile']").length != 0 ||
                $(this).find("input[name='outputFormat']").length != 0 ){
                // Remove it
                $(this).remove();
            }
        });
    }
});

// Rdf Store Settings
//
// In waves, we support two types of triple store
//   - sesame
//   - virtuoso
//
// If user choose virtuoso as their triple store, 
//   there will be 3 more settings:
//   - login
//   - password
//   - Endpoint
//
// We need to show these 3 settings when user choose choose virtuoso, 
//   and remove them if he chooses sesame
//
// We will also update the default value of triple store location
//   when user change the choice of triple store type
//
$("form[type='RdfStoreSettings'] input[name='storeType']").on("change", function(){

    console.log("Change the choice of rdf store type");

    // If user choose Virtuoso
    if( $(this).val() == "virtuoso" ){
        // Insert some configuration inputs for virtuoso settings
        var $virtuosoConfigInputs = $(`
          <div class="form-group">
            <label class="control-label col-sm-2" for="login">Triple Store Login :</label>
            <div class="col-sm-6">
                <input class="form-control" name="login" type="text" placeholder="username" value="dba">
                <small class="text-muted">Enter the username of Triple Store Repository.</small>
            </div>
          </div>
          <div class="form-group">
            <label class="control-label col-sm-2" for="password">Password :</label>
            <div class="col-sm-6">
                <input class="form-control" name="password" type="password" placeholder="password" value="dba">
                <small class="text-muted">Enter the password</small>
            </div>
          </div>
          <div class="form-group">
            <label class="control-label col-sm-2" for="endpoint">Endpoint :</label>
            <div class="col-sm-6">
                <input class="form-control" name="endpoint" type="text" placeholder="http://localhost:8890/sparql" value="http://localhost:8890/sparql">
                <small class="text-muted">Enter the endpoint of Triple Store.</small>
            </div>
          </div>
        `);
        // Append the input fields after selection
        $virtuosoConfigInputs.insertAfter($(this).closest(".form-group"));
        
        // Get current form
        var $form = $(this).closest("form");
        // Iterate each form group of the rdf store settings form
        $form.children(".form-group").each(function(){
            // Find the input field of location panel
            if( $(this).find("input[name='location']").length != 0 ){
                // Set the input field value as default virtuoso location
                $(this).find("input[name='location']").val("jdbc:virtuoso://localhost:1111");
            }
        });
    } else {
        // If user choose sesame
        var $form = $(this).closest("form");
        // Iterate each form group of the rdf store settings form
        $form.children(".form-group").each(function(){
            // Remove the 3 input fields of sesame config settings
            if( $(this).find("input[name='login']").length != 0 ||
                $(this).find("input[name='password']").length != 0 ||
                $(this).find("input[name='endpoint']").length != 0 ){
                // Remove it
                $(this).remove();
            }
            
            // Find the triple store location input field
            if( $(this).find("input[name='location']").length != 0 ){
                // Change the default value
                $(this).find("input[name='location']").val("http://localhost:9091/openrdf-sesame/repositories/waves");
            }
        });
    }
});

// ----------------------------------------
// Hide & Show some Advanced Settings for Strider
// ----------------------------------------

// For Strider, there're some advanced settings
//   which are not user friendly to be shown directly to users
// Click on the button to toogle these settings
$("form[type='StriderSettings'] button[name='toggleAdvancedSettings']").click(function(e){
    e.preventDefault();
    $form = $(this).closest('form');
    $form.find('div.advanced-settings').toggleClass('hide');
});

// ----------------------------------------
// Delete component & Detach Connections
// ----------------------------------------

// Click "Detach Conn." button to detach connections
$("button[name='detachConns']").click(function(e){
    e.preventDefault();
    var cmpt_id = $(this).closest('form').attr('cmpt_id');
    var conns = jsPlumb.getConnections({
        source: cmpt_id
    });
    for(var conn of conns) {
        jsPlumb.detach(conn);
        delConns(cmpt_id);
    }
});

// Tell the server to delete links
function delConns(srcCmptId){
    var data = new FormData();
    data.append('srcCmptId', srcCmptId);
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/remove-link", true);
    xhr.send(data);    
}

// Click "Delete Component" button to delete component
$('button[name="deleteCmpt"]').click(function(e){
    e.preventDefault();
    var cmpt_id = $(this).closest('form').attr('cmpt_id');
    jsPlumb.remove(cmpt_id);
    delCmpt(cmpt_id);
    
    $form = $(this).closest('form').addClass('hide');
    $form.siblings('h5').removeClass('hide');
});

// delete all components
$('#delete_all_workflow').click(function(e){
    e.preventDefault();
    $('#panel').find(".component").each(function(){
        var cmpt_id = $(this).attr("id");
        jsPlumb.remove(cmpt_id);
        delCmpt(cmpt_id);
    });
});

// Tell the server to delete components
function delCmpt(cmpt_id){
    var data = new FormData();
    data.append('id', cmpt_id);
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/remove-component", true);
    xhr.send(data);    
}
    
// ----------------------------------------
// Upload Files
// ----------------------------------------
    
// Click button to upload single file
// Upload dataset using fileinput API
// Upload single file for static feed
$("form[type='RdfFeedSettings'] input[name='location']").fileinput({
    uploadUrl: "/create-project/upload-single-file", // server upload action
    uploadAsync: true
});

// Upload multi files
// Upload multi files for rdf sources to generate rdf stream
$("form[type='SourceSettings'] input[name='inputFolder']").fileinput({
    uploadUrl: "/create-project/upload-multi-file", // server upload action
    uploadAsync: true,
    browseLabel: 'Select Multi Files ...'
});
 
// Upload multi files for raw source to generate raw stream
$("form[type='RawSourceSettings'] input[name='location']").fileinput({
    uploadUrl: "/create-project/upload-multi-file", // server upload action
    uploadAsync: true,
    browseLabel: 'Select Multi Files ...'
});  

    
// ----------------------------------------
// Generate TriG and Create Project
// ----------------------------------------

// Only preview trig
$('#preview_trig').click(function(event){
    event.preventDefault();
    
    // Get Form Data from Panel 1 and Panel 3
    var form_data = new FormData();
    // panel 1
    $('#project_form').serializeArray().reduce(function(obj, item) {
        form_data.append( item.name, item.value );
    }, {});
    // panel 3
    $('#monitoring_form').serializeArray().reduce(function(obj, item) {
        form_data.append( item.name, item.value );
    }, {});
    
    // Send request and ask for TRIG string
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project/preview-trig", true);
    xhr.onreadystatechange = (event) => {
      if (xhr.readyState == XMLHttpRequest.DONE) {
          res = JSON.parse( xhr.responseText );
          $("#trig_content").text(res['trig']);
          $("#trigModal").modal();
      }
    }
    xhr.send(form_data);
});

// Create Project
$('#create').click(function(event){
    event.preventDefault();
    
    // Get Form Data
    var form_data = new FormData();
    $('#project_form').serializeArray().reduce(function(obj, item) {
        form_data.append( item.name, item.value );
    }, {});
    $('#monitoring_form').serializeArray().reduce(function(obj, item) {
        form_data.append( item.name, item.value );
    }, {});
    
    // Get the html workflow project configuration
    var workflow_ui = $('#panel').html();
    console.log(workflow_ui);
    form_data.append("workflow_ui", workflow_ui);
    
    // Send request and save the workflow of the project
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-project", true);
    xhr.onreadystatechange = (event) => {
      if (xhr.readyState == XMLHttpRequest.DONE) {
          console.log(xhr.responseText);
          bootbox.alert("Success: Your project has been saved!");
      }
    }
    xhr.onerror = (event) => {
        bootbox.alert("Sorry: Can not submit your project due to some errors!");
    }
    xhr.send(form_data);
});