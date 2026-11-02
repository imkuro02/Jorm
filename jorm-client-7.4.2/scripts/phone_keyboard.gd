extends Node

func _ready():
	if OS.has_feature("web"):
		JavaScriptBridge.eval("""
			window.openMobileKeyboard = function() {
				let input = document.getElementById("jorm-mobile-input");
				if (input) {
					input.focus();
				}
			};
		""")

func open_mobile_keyboard():
	if OS.has_feature("web"):
		JavaScriptBridge.eval("""
			let input = document.getElementById("jorm-mobile-input");
			if (input) {
				input.focus();
			}
		""")
