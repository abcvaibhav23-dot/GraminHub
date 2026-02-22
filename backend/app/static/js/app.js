let supplierCache = {};
let currentUserRole = "guest";

const UI_LANG_STORAGE_KEY = "ui_lang_mode";

const uiText = {
  hinglish: {
    nav_home: "होम",
    nav_login: "लॉगिन",
    nav_register: "रजिस्टर",
    nav_profile: "प्रोफाइल",
    nav_logout: "लॉगआउट",
    nav_role_prefix: "भूमिका:",
    nav_dashboard_admin: "Admin डैशबोर्ड",
    nav_dashboard_supplier: "Supplier डैशबोर्ड",
    footer_tagline: "तेज सप्लायर खोज, बुकिंग और WhatsApp कन्वर्जन के लिए बनाया गया प्लेटफॉर्म।",
    brand_network_tagline: "गांव-कस्बा सप्लायर नेटवर्क",

    role_guest: "मेहमान",
    role_user: "यूज़र",
    role_supplier: "सप्लायर",
    role_admin: "एडमिन",
    auth_session_expired: "सेशन समाप्त/अमान्य है। कृपया दोबारा लॉगिन करें।",
    admin_auth_required: "यह क्रिया केवल Admin लॉगिन से उपलब्ध है।",
    supplier_auth_required: "यह क्रिया Supplier/Admin लॉगिन से उपलब्ध है।",
    error_supplier_id_required: "कृपया Supplier ID दर्ज करें।",
    error_service_id_required: "कृपया Service ID दर्ज करें।",
    error_user_id_required: "कृपया User ID दर्ज करें।",
    error_category_name_required: "कृपया Category नाम दर्ज करें।",
    error_invalid_category_id: "कृपया सही Category ID दर्ज करें।",
    error_invalid_price: "कृपया सही कीमत दर्ज करें।",
    error_profile_fields_required: "प्रोफाइल अपडेट के लिए कम से कम एक वैल्यू दें।",
    error_supplier_profile_fields_required: "Supplier प्रोफाइल अपडेट के लिए सभी फ़ील्ड भरें।",
    error_supplier_service_update_fields_required: "सेवा अपडेट के लिए category, price या availability में से कोई एक दें।",

    home_badge: "भरोसेमंद ग्रामीण मार्केटप्लेस",
    home_title: "अब गांव से ही सप्लायर, वाहन और रेंटल सेवा तुरंत बुक करें",
    home_desc:
      "GraminHub पर Construction Materials, Heavy Vehicles, Transport Vehicles और Equipment Rentals जैसी सेवाएं एक ही जगह मिलती हैं।",
    home_logged_in_as: "लॉगिन यूज़र:",
    home_booking_mode: "बुकिंग: Call + WhatsApp",
    home_search_title: "तुरंत खोजें और बुक करें",
    home_search_desc:
      "Category चुनें, अपनी जरूरत लिखें, सप्लायर खोजें और WhatsApp से बुकिंग शुरू करें।",
    home_category_label: "श्रेणी (Category)",
    home_query_label: "सप्लायर खोजें (नाम/स्थान/मोबाइल)",
    home_query_placeholder: "उदाहरण: Sonbhadra, JCB, 98765...",
    home_requirement_label: "आपकी जरूरत",
    home_requirement_placeholder: "उदाहरण: सोनभद्र में 2 दिन के लिए ट्रैक्टर ट्रॉली चाहिए",
    home_search_btn: "सप्लायर खोजें",
    home_booking_note_prefix:
      "आप बिना लॉगिन भी बुकिंग कर सकते हैं (नाम + मोबाइल देकर)। लॉगिन करने पर",
    home_booking_note_suffix: "भूमिका से और बेहतर ट्रैकिंग मिलेगी।",
    home_available_title: "उपलब्ध सप्लायर",
    home_available_desc: "सीधा फोन करने के लिए Call दबाएं या WhatsApp से बुकिंग शुरू करें।",
    home_console_title: "लाइव एक्टिविटी कंसोल",
    home_console_desc: "खोज, कॉल और बुकिंग के दौरान API रिस्पॉन्स यहां दिखेगा।",
    home_owner_title: "ओनर/सपोर्ट संपर्क",
    home_owner_desc: "कोई समस्या हो तो सीधे संपर्क करें:",
    home_owner_email: "ईमेल:",
    home_owner_whatsapp: "WhatsApp:",

    home_feature_category_label: "श्रेणी",
    home_feature_materials_desc: "सीमेंट, गिट्टी, बालू, स्टील और साइट का पूरा सामान।",
    home_feature_heavy_desc: "JCB, Excavator, Loader जैसी भारी मशीनरी बुकिंग।",
    home_feature_transport_desc: "Truck, mini-truck और स्थानीय लॉजिस्टिक्स सपोर्ट।",
    home_feature_rental_desc: "छोटे और लंबे समय के लिए उपकरण किराये पर।",

    category_all: "सभी श्रेणियां",
    home_no_suppliers: "इस श्रेणी में अभी कोई approved सप्लायर नहीं मिला।",
    home_supplier_verified: "Verified सप्लायर",
    home_supplier_id_prefix: "आईडी",
    home_contact_number: "संपर्क नंबर:",
    home_rating_label: "रेटिंग:",
    home_reviews_suffix: "रिव्यू",
    home_call_btn: "कॉल करें",
    home_book_whatsapp_btn: "WhatsApp से बुक करें",
    home_rate_btn: "रेटिंग दें",

    action_ready: "तैयार",
    action_guest_direct_call: "बिना लॉगिन आप सीधे कॉल कर सकते हैं: {phone}",
    action_supplier_phone_unavailable: "सप्लायर फोन उपलब्ध नहीं है।",
    action_call_logged: "Supplier #{supplierId} के लिए कॉल लॉग हो गई। फोन: {phone}",
    action_supplier_missing_refresh: "सप्लायर की जानकारी उपलब्ध नहीं है। रिफ्रेश करके फिर प्रयास करें।",
    prompt_guest_name: "बुकिंग के लिए अपना नाम लिखें:",
    error_guest_name: "नाम कम से कम 2 अक्षरों का होना चाहिए।",
    prompt_guest_phone: "अपना मोबाइल नंबर लिखें:",
    error_guest_phone: "सही मोबाइल नंबर लिखें।",
    action_booking_created_whatsapp: "बुकिंग #{bookingId} बन गई। सप्लायर फोन {phone} के लिए WhatsApp खुल रहा है।",
    error_login_for_rating: "रेटिंग देने के लिए पहले लॉगिन करें।",
    prompt_rating: "रेटिंग दें (1 से 5):",
    error_rating_range: "रेटिंग 1 से 5 के बीच पूरी संख्या होनी चाहिए।",
    prompt_comment: "छोटी टिप्पणी लिखें:",
    error_comment_min: "टिप्पणी कम से कम 2 अक्षरों की होनी चाहिए।",
    action_rating_saved: "Supplier #{supplierId} के लिए आपकी रेटिंग सेव हो गई।",
    default_booking_desc: "{businessName} से सेवा बुक करनी है",

    brand_subtitle: "भरोसेमंद ग्रामीण सेवा मंच",
    secure_badge: "Secure Login",
    hero_title: "लॉगिन करें और अपनी बुकिंग प्रक्रिया आसानी से जारी रखें",
    hero_desc: "यहां से आप सप्लायर खोज, कॉल, WhatsApp बुकिंग और डैशबोर्ड एक्सेस एक ही जगह से कंट्रोल कर सकते हैं।",
    stat_1: "मुख्य श्रेणियां",
    stat_2: "बुकिंग रिक्वेस्ट",
    stat_3: "WhatsApp संपर्क",
    point_1: "नेवबार में आपकी भूमिका (Role) तुरंत दिखाई देगी",
    point_2: "सप्लायर से सीधा Call या WhatsApp बुकिंग संभव",
    point_3: "User, Supplier, Admin सभी workflows और free stack समर्थित",
    form_title: "साइन इन",
    form_desc: "अपना रजिस्टर्ड ईमेल और पासवर्ड दर्ज करें।",
    email_label: "ईमेल",
    email_placeholder: "name@example.com",
    password_label: "पासवर्ड",
    password_placeholder: "पासवर्ड दर्ज करें",
    login_button: "लॉगिन करें",
    token_note: "इस MVP डेमो में टोकन localStorage में सेव होता है।",
    result_waiting: "प्रतीक्षा...",
    no_account: "अकाउंट नहीं है?",
    register_now: "अभी रजिस्टर करें",

    register_title: "नया अकाउंट बनाएं",
    register_desc: "एक बार रजिस्टर करें और सप्लायर खोज व बुकिंग शुरू करें।",
    register_name_label: "पूरा नाम",
    register_name_placeholder: "अपना पूरा नाम लिखें",
    register_email_label: "ईमेल",
    register_email_placeholder: "name@example.com",
    register_password_label: "पासवर्ड",
    register_password_placeholder: "नया पासवर्ड बनाएं",
    register_role_label: "भूमिका (Role)",
    register_role_user: "User (ग्राहक)",
    register_role_supplier: "Supplier (विक्रेता)",
    register_role_admin: "Admin (प्रशासन)",
    register_button: "रजिस्टर करें",
    register_has_account: "पहले से अकाउंट है?",
    register_login_now: "लॉगिन करें",
    register_panel_title: "अपने काम के हिसाब से सही भूमिका चुनें",
    register_panel_user_title: "User (ग्राहक)",
    register_panel_user_desc: "सप्लायर खोजें, बुकिंग बनाएं और तुरंत WhatsApp चैट शुरू करें।",
    register_panel_supplier_title: "Supplier (विक्रेता)",
    register_panel_supplier_desc: "प्रोफाइल बनाएं, रेट सहित सेवाएं जोड़ें और बुकिंग संभालें।",
    register_panel_admin_title: "Admin (प्रशासन)",
    register_panel_admin_desc: "सप्लायर अप्रूवल, नई कैटेगरी और पूरी गतिविधि मॉनिटर करें।",

    profile_title: "प्रोफाइल सेटिंग्स",
    profile_desc: "नाम, ईमेल और पासवर्ड अपडेट करें। यह विकल्प User, Supplier और Admin सभी के लिए है।",
    profile_name_label: "नाम",
    profile_name_placeholder: "अपना नाम",
    profile_email_label: "ईमेल",
    profile_email_placeholder: "name@example.com",
    profile_password_label: "नया पासवर्ड (optional)",
    profile_password_placeholder: "खाली छोड़ें अगर पासवर्ड नहीं बदलना",
    profile_save_btn: "प्रोफाइल सेव करें",
    profile_close_btn: "बंद करें",

    supplier_dash_title: "Supplier डैशबोर्ड",
    supplier_dash_subtitle:
      "WhatsApp नंबर सहित प्रोफाइल पूरी करें, सेवाओं का रेट जोड़ें और आने वाली बुकिंग रिक्वेस्ट देखें।",
    supplier_profile_title: "Supplier प्रोफाइल",
    supplier_profile_desc: "Admin approval के बाद यह प्रोफाइल यूज़र्स को दिखेगी।",
    supplier_profile_business_placeholder: "व्यवसाय का नाम",
    supplier_profile_phone_placeholder: "फोन नंबर (WhatsApp चालू)",
    supplier_profile_address_placeholder: "व्यवसाय का पता",
    supplier_profile_save_btn: "प्रोफाइल सेव करें",
    supplier_profile_saved_with_id: "प्रोफाइल सेव हो गई। Admin approval के लिए Supplier ID: {supplierId}",
    supplier_service_title: "सेवा और कीमत जोड़ें",
    supplier_service_desc: "Category-wise सेवाएं जोड़ें ताकि यूज़र आपकी लिस्टिंग देख सकें।",
    supplier_service_category_placeholder: "Category ID (जैसे 2)",
    supplier_service_price_placeholder: "कीमत",
    supplier_service_availability_placeholder: "उपलब्धता (available/on request)",
    supplier_service_add_btn: "सेवा जोड़ें",
    supplier_manage_title: "जुड़े हुए रिकॉर्ड एडिट करें",
    supplier_manage_desc: "अपने पुराने Supplier प्रोफाइल और जोड़ी गई सेवाएं ID से अपडेट करें।",
    supplier_manage_load_profiles_btn: "मेरे प्रोफाइल लोड करें",
    supplier_manage_supplier_id_placeholder: "Supplier ID",
    supplier_manage_update_profile_btn: "Supplier प्रोफाइल अपडेट करें",
    supplier_manage_load_services_btn: "मेरी सेवाएं लोड करें",
    supplier_manage_service_id_placeholder: "Service ID",
    supplier_manage_update_service_btn: "सेवा अपडेट करें",
    supplier_activity_title: "Supplier गतिविधि",
    supplier_activity_desc: "प्रोफाइल/सेवा अपडेट का API रिस्पॉन्स यहां देखें।",
    supplier_activity_waiting: "रिस्पॉन्स यहां दिखेगा...",
    supplier_incoming_title: "आने वाली बुकिंग रिक्वेस्ट",
    supplier_incoming_desc: "यूज़र्स की नई बुकिंग रिक्वेस्ट यहां देखें।",
    supplier_refresh_btn: "रिफ्रेश",

    admin_dash_title: "Admin कंट्रोल टॉवर",
    admin_dash_desc: "सप्लायर अप्रूवल, नई कैटेगरी और सभी बुकिंग गतिविधियां एक ही स्क्रीन से मैनेज करें।",
    admin_approval_title: "Supplier अप्रूवल",
    admin_approval_desc: "वेरिफिकेशन के बाद Supplier ID डालकर approve करें।",
    admin_supplier_id_placeholder: "Supplier ID",
    admin_approve_btn: "Approve करें",
    admin_category_title: "नई Category जोड़ें",
    admin_category_desc: "मार्केटप्लेस विस्तार के लिए नई श्रेणी बनाएं।",
    admin_category_placeholder: "Category नाम",
    admin_category_btn: "Category बनाएं",
    admin_block_title: "Supplier Block/Unblock",
    admin_block_desc: "खराब रेटिंग या खराब सेवा पर Supplier को block करें, सुधार होने पर unblock करें।",
    admin_block_btn: "Block करें",
    admin_unblock_btn: "Unblock करें",
    admin_delete_title: "Delete Supplier/User",
    admin_delete_desc: "जरूरत होने पर Supplier ID या User ID हटाएं। यह action permanent है।",
    admin_user_id_placeholder: "User ID",
    admin_delete_supplier_btn: "Delete Supplier",
    admin_delete_user_btn: "Delete User",
    admin_delete_supplier_confirm: "क्या आप इस Supplier को permanent delete करना चाहते हैं?",
    admin_delete_user_confirm: "क्या आप इस User को permanent delete करना चाहते हैं?",
    admin_pending_btn: "Pending Suppliers",
    admin_all_bookings_btn: "सभी बुकिंग",
    admin_pending_empty: "कोई pending supplier नहीं है।",
    admin_pending_hint: "Approve/Block के लिए नीचे दिखा Supplier ID ही उपयोग करें:",
    admin_pending_item: "Supplier ID: {supplierId} | नाम: {businessName} | फोन: {phone}",
  },
  english: {
    nav_home: "Home",
    nav_login: "Login",
    nav_register: "Register",
    nav_profile: "Profile",
    nav_logout: "Logout",
    nav_role_prefix: "Role:",
    nav_dashboard_admin: "Admin Dashboard",
    nav_dashboard_supplier: "Supplier Dashboard",
    footer_tagline:
      "Built for fast supplier discovery, booking, and WhatsApp conversion.",
    brand_network_tagline: "Village-Town Supplier Network",

    role_guest: "Guest",
    role_user: "User",
    role_supplier: "Supplier",
    role_admin: "Admin",
    auth_session_expired: "Session expired or invalid. Please log in again.",
    admin_auth_required: "This action is available only for Admin login.",
    supplier_auth_required: "This action is available for Supplier/Admin login only.",
    error_supplier_id_required: "Please enter a Supplier ID.",
    error_service_id_required: "Please enter a Service ID.",
    error_user_id_required: "Please enter a User ID.",
    error_category_name_required: "Please enter a category name.",
    error_invalid_category_id: "Please enter a valid category ID.",
    error_invalid_price: "Please enter a valid price.",
    error_profile_fields_required: "Enter at least one value to update your profile.",
    error_supplier_profile_fields_required: "Fill all fields to update supplier profile.",
    error_supplier_service_update_fields_required: "Provide at least one of category, price, or availability.",

    home_badge: "Verified Rural Marketplace",
    home_title: "Book suppliers, vehicles, and rentals quickly from your village",
    home_desc:
      "GraminHub brings Construction Materials, Heavy Vehicles, Transport Vehicles, and Equipment Rentals together in one place.",
    home_logged_in_as: "Logged in user:",
    home_booking_mode: "Booking: Call + WhatsApp",
    home_search_title: "Search and Book Instantly",
    home_search_desc:
      "Select category, write your requirement, find suppliers, and start booking on WhatsApp.",
    home_category_label: "Category",
    home_query_label: "Search supplier (name/location/mobile)",
    home_query_placeholder: "Example: Sonbhadra, JCB, 98765...",
    home_requirement_label: "Your Requirement",
    home_requirement_placeholder: "Example: Need tractor with trolley for 2 days in Sonbhadra",
    home_search_btn: "Search Suppliers",
    home_booking_note_prefix:
      "You can also book without login (with name + mobile). With login as",
    home_booking_note_suffix: "role, tracking is better.",
    home_available_title: "Available Suppliers",
    home_available_desc: "Tap Call for direct contact or WhatsApp to start booking.",
    home_console_title: "Live Activity Console",
    home_console_desc: "API responses appear here while searching, calling, and booking.",
    home_owner_title: "Owner/Support Contact",
    home_owner_desc: "For any issue, contact directly:",
    home_owner_email: "Email:",
    home_owner_whatsapp: "WhatsApp:",

    home_feature_category_label: "Category",
    home_feature_materials_desc: "Cement, aggregate, sand, steel, and complete site materials.",
    home_feature_heavy_desc: "Book heavy machinery like JCB, Excavator, and Loader.",
    home_feature_transport_desc: "Truck, mini-truck, and local logistics support.",
    home_feature_rental_desc: "Equipment rentals for short and long durations.",

    category_all: "All Categories",
    home_no_suppliers: "No approved suppliers found in this category yet.",
    home_supplier_verified: "Verified Supplier",
    home_supplier_id_prefix: "ID",
    home_contact_number: "Contact Number:",
    home_rating_label: "Rating:",
    home_reviews_suffix: "reviews",
    home_call_btn: "Call",
    home_book_whatsapp_btn: "Book on WhatsApp",
    home_rate_btn: "Rate Supplier",

    action_ready: "Ready",
    action_guest_direct_call: "You can directly call without login: {phone}",
    action_supplier_phone_unavailable: "Supplier phone is not available.",
    action_call_logged: "Call has been logged for supplier #{supplierId}. Phone: {phone}",
    action_supplier_missing_refresh: "Supplier details are unavailable. Refresh and try again.",
    prompt_guest_name: "Enter your name for booking:",
    error_guest_name: "Name should be at least 2 characters.",
    prompt_guest_phone: "Enter your mobile number:",
    error_guest_phone: "Enter a valid mobile number.",
    action_booking_created_whatsapp: "Booking #{bookingId} created. Opening WhatsApp for supplier phone {phone}.",
    error_login_for_rating: "Please log in before rating.",
    prompt_rating: "Give rating (1 to 5):",
    error_rating_range: "Rating must be an integer between 1 and 5.",
    prompt_comment: "Write a short comment:",
    error_comment_min: "Comment should be at least 2 characters.",
    action_rating_saved: "Your rating is saved for supplier #{supplierId}.",
    default_booking_desc: "Need service from {businessName}",

    brand_subtitle: "Trusted Rural Service Platform",
    secure_badge: "Secure Login",
    hero_title: "Log in and continue your booking workflow smoothly",
    hero_desc: "From here you can search suppliers, place calls, start WhatsApp booking, and access dashboards in one place.",
    stat_1: "Core Categories",
    stat_2: "Booking Requests",
    stat_3: "WhatsApp Connect",
    point_1: "Your role is shown live in the navbar",
    point_2: "Direct Call and WhatsApp booking with suppliers",
    point_3: "Supports User, Supplier, Admin workflows on a free stack",
    form_title: "Sign In",
    form_desc: "Use your registered email and password.",
    email_label: "Email",
    email_placeholder: "name@example.com",
    password_label: "Password",
    password_placeholder: "Enter your password",
    login_button: "Login",
    token_note: "For this MVP demo, the token is stored in localStorage.",
    result_waiting: "Waiting...",
    no_account: "No account?",
    register_now: "Register now",

    register_title: "Create a New Account",
    register_desc: "Register once and start supplier search and booking.",
    register_name_label: "Full Name",
    register_name_placeholder: "Enter your full name",
    register_email_label: "Email",
    register_email_placeholder: "name@example.com",
    register_password_label: "Password",
    register_password_placeholder: "Create a new password",
    register_role_label: "Role",
    register_role_user: "User (Buyer)",
    register_role_supplier: "Supplier (Seller)",
    register_role_admin: "Admin",
    register_button: "Register",
    register_has_account: "Already have an account?",
    register_login_now: "Login",
    register_panel_title: "Choose the right role for your work",
    register_panel_user_title: "User (Buyer)",
    register_panel_user_desc: "Find suppliers, create bookings, and start WhatsApp chat instantly.",
    register_panel_supplier_title: "Supplier (Seller)",
    register_panel_supplier_desc: "Create profile, add priced services, and manage bookings.",
    register_panel_admin_title: "Admin",
    register_panel_admin_desc: "Manage supplier approvals, categories, and full platform activity.",

    profile_title: "Profile Settings",
    profile_desc: "Update your name, email, and password. Available for User, Supplier, and Admin.",
    profile_name_label: "Name",
    profile_name_placeholder: "Enter your name",
    profile_email_label: "Email",
    profile_email_placeholder: "name@example.com",
    profile_password_label: "New Password (optional)",
    profile_password_placeholder: "Leave blank if you do not want to change password",
    profile_save_btn: "Save Profile",
    profile_close_btn: "Close",

    supplier_dash_title: "Supplier Dashboard",
    supplier_dash_subtitle:
      "Complete your profile with WhatsApp number, add service pricing, and monitor incoming booking requests.",
    supplier_profile_title: "Supplier Profile",
    supplier_profile_desc: "After admin approval, this profile is shown to users.",
    supplier_profile_business_placeholder: "Business name",
    supplier_profile_phone_placeholder: "Phone number (WhatsApp active)",
    supplier_profile_address_placeholder: "Business address",
    supplier_profile_save_btn: "Save Profile",
    supplier_profile_saved_with_id: "Profile saved. Use this Supplier ID for admin approval: {supplierId}",
    supplier_service_title: "Add Service and Price",
    supplier_service_desc: "Add category-wise services so users can find your listing.",
    supplier_service_category_placeholder: "Category ID (e.g. 2)",
    supplier_service_price_placeholder: "Price",
    supplier_service_availability_placeholder: "Availability (available/on request)",
    supplier_service_add_btn: "Add Service",
    supplier_manage_title: "Edit Existing Records",
    supplier_manage_desc: "Update your existing supplier profiles and added services by ID.",
    supplier_manage_load_profiles_btn: "Load My Profiles",
    supplier_manage_supplier_id_placeholder: "Supplier ID",
    supplier_manage_update_profile_btn: "Update Supplier Profile",
    supplier_manage_load_services_btn: "Load My Services",
    supplier_manage_service_id_placeholder: "Service ID",
    supplier_manage_update_service_btn: "Update Service",
    supplier_activity_title: "Supplier Activity",
    supplier_activity_desc: "View API responses for profile/service updates here.",
    supplier_activity_waiting: "Response will appear here...",
    supplier_incoming_title: "Incoming Booking Requests",
    supplier_incoming_desc: "View fresh user booking requests here.",
    supplier_refresh_btn: "Refresh",

    admin_dash_title: "Admin Control Tower",
    admin_dash_desc: "Manage supplier approvals, new categories, and all booking activity from one screen.",
    admin_approval_title: "Supplier Approval",
    admin_approval_desc: "After verification, enter Supplier ID and approve.",
    admin_supplier_id_placeholder: "Supplier ID",
    admin_approve_btn: "Approve",
    admin_category_title: "Add New Category",
    admin_category_desc: "Create new categories for marketplace expansion.",
    admin_category_placeholder: "Category name",
    admin_category_btn: "Create Category",
    admin_block_title: "Supplier Block/Unblock",
    admin_block_desc: "Block suppliers for poor service and unblock after correction.",
    admin_block_btn: "Block",
    admin_unblock_btn: "Unblock",
    admin_delete_title: "Delete Supplier/User",
    admin_delete_desc: "Delete Supplier ID or User ID when required. This action is permanent.",
    admin_user_id_placeholder: "User ID",
    admin_delete_supplier_btn: "Delete Supplier",
    admin_delete_user_btn: "Delete User",
    admin_delete_supplier_confirm: "Do you want to permanently delete this supplier?",
    admin_delete_user_confirm: "Do you want to permanently delete this user?",
    admin_pending_btn: "Pending Suppliers",
    admin_all_bookings_btn: "All Bookings",
    admin_pending_empty: "No pending suppliers found.",
    admin_pending_hint: "Use only the Supplier ID shown below for Approve/Block actions:",
    admin_pending_item: "Supplier ID: {supplierId} | Name: {businessName} | Phone: {phone}",
  },
};

function formatMessage(template, values = {}) {
  return Object.entries(values).reduce(
    (message, [key, value]) => message.replaceAll(`{${key}}`, String(value)),
    template,
  );
}

function getLangMode() {
  return localStorage.getItem(UI_LANG_STORAGE_KEY) === "english" ? "english" : "hinglish";
}

function t(key) {
  const mode = getLangMode();
  return uiText[mode][key] ?? uiText.hinglish[key] ?? key;
}

function roleLabel(role) {
  const normalized = role || "guest";
  if (normalized === "user") return t("role_user");
  if (normalized === "supplier") return t("role_supplier");
  if (normalized === "admin") return t("role_admin");
  return t("role_guest");
}

function setLanguageButtonState(mode) {
  const defaultBtn = document.getElementById("langHinglish");
  const englishBtn = document.getElementById("langEnglish");
  if (!defaultBtn || !englishBtn) return;

  if (mode === "english") {
    defaultBtn.className = "rounded-full border border-slate-300 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-700";
    englishBtn.className = "rounded-full border border-brand-200 bg-brand-50 px-2.5 py-1 text-[11px] font-semibold text-brand-700";
  } else {
    defaultBtn.className = "rounded-full border border-brand-200 bg-brand-50 px-2.5 py-1 text-[11px] font-semibold text-brand-700";
    englishBtn.className = "rounded-full border border-slate-300 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-700";
  }
}

function applyLanguage(mode) {
  const normalized = mode === "english" ? "english" : "hinglish";
  const texts = uiText[normalized];
  if (!texts) return;

  document.querySelectorAll("[data-login-i18n], [data-ui-i18n]").forEach((el) => {
    const key = el.getAttribute("data-login-i18n");
    const uiKey = el.getAttribute("data-ui-i18n");
    const lookup = key || uiKey;
    if (lookup && texts[lookup] !== undefined) {
      const dynamicStatusKeys = ["result_waiting", "action_ready", "supplier_activity_waiting"];
      if (dynamicStatusKeys.includes(lookup)) {
        const currentValue = (el.textContent || "").trim();
        if (currentValue) {
          const localizedDefaults = Object.values(uiText)
            .map((langText) => (langText[lookup] || "").trim())
            .filter(Boolean);
          if (!localizedDefaults.includes(currentValue)) {
            return;
          }
        }
      }
      el.textContent = texts[lookup];
    }
  });

  document.querySelectorAll("[data-login-placeholder], [data-ui-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-login-placeholder");
    const uiKey = el.getAttribute("data-ui-placeholder");
    const lookup = key || uiKey;
    if (lookup && texts[lookup] !== undefined) {
      el.setAttribute("placeholder", texts[lookup]);
    }
  });

  document.querySelectorAll("[data-ui-option], [data-login-option]").forEach((el) => {
    const key = el.getAttribute("data-login-option");
    const uiKey = el.getAttribute("data-ui-option");
    const lookup = key || uiKey;
    if (lookup && texts[lookup] !== undefined) {
      el.textContent = texts[lookup];
    }
  });

  document.documentElement.setAttribute("lang", normalized === "english" ? "en" : "hi");
  localStorage.setItem(UI_LANG_STORAGE_KEY, normalized);
  setLanguageButtonState(normalized);

  updateRoleUI({ role: currentUserRole });

  if (document.getElementById("supplierCards") && Object.keys(supplierCache).length > 0) {
    renderSuppliers(Object.values(supplierCache));
  }

  if (document.getElementById("categorySelect")) {
    loadCategories();
  }
}

function initLanguageToggle() {
  const defaultBtn = document.getElementById("langHinglish");
  const englishBtn = document.getElementById("langEnglish");
  if (!defaultBtn || !englishBtn) return;

  const savedMode = getLangMode();
  applyLanguage(savedMode);

  defaultBtn.addEventListener("click", () => applyLanguage("hinglish"));
  englishBtn.addEventListener("click", () => applyLanguage("english"));
}

function authHeader() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function ratingStars(value) {
  const safe = Math.max(0, Math.min(5, Number(value || 0)));
  const rounded = Math.round(safe);
  return `${"★".repeat(rounded)}${"☆".repeat(5 - rounded)}`;
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.remove("hidden");
    el.textContent = value;
  }
}

function setJSON(id, value) {
  const payload =
    value && typeof value === "object" && value.data !== undefined ? value.data : value;
  setText(id, JSON.stringify(payload, null, 2));
}

async function requestJSON(path, options = {}) {
  try {
    const res = await fetch(path, {
      headers: {
        "Content-Type": "application/json",
        ...authHeader(),
        ...(options.headers || {}),
      },
      ...options,
    });
    const data = await res.json().catch(() => ({ detail: "No JSON response" }));
    return { status: res.status, data };
  } catch (error) {
    return {
      status: 0,
      data: {
        detail: "Server connect issue. Ensure backend is running on http://localhost:8000",
      },
    };
  }
}

function dashboardPathForRole(role) {
  if (role === "admin") return "/admin-dashboard";
  if (role === "supplier") return "/supplier-dashboard";
  return "/";
}

function canAccessCurrentPage(role) {
  const path = window.location.pathname;
  if (path === "/admin-dashboard") return role === "admin";
  if (path === "/supplier-dashboard") return role === "supplier" || role === "admin";
  return true;
}

function enforcePageAccess(user) {
  const role = user && user.role ? user.role : "guest";
  if (!canAccessCurrentPage(role)) {
    window.location.href = "/login";
  }
}

function setNavItemActive(navItem, isActive) {
  if (!navItem || navItem.classList.contains("hidden")) return;

  if (isActive) {
    navItem.classList.remove("text-slate-700", "hover:bg-slate-100");
    navItem.classList.add("bg-brand-600", "text-white", "hover:bg-brand-700");
    return;
  }

  navItem.classList.remove("bg-brand-600", "text-white", "hover:bg-brand-700");
  navItem.classList.add("text-slate-700", "hover:bg-slate-100");
}

function updateNavActiveState() {
  const path = window.location.pathname;

  const navHome = document.getElementById("navHome");
  const navLogin = document.getElementById("navLogin");
  const navRegister = document.getElementById("navRegister");
  const navProfile = document.getElementById("navProfile");
  const navDashboard = document.getElementById("navDashboard");

  setNavItemActive(navHome, path === "/");
  setNavItemActive(navLogin, path === "/login");
  setNavItemActive(navRegister, path === "/register");
  setNavItemActive(navProfile, false);

  const onDashboard = path === "/supplier-dashboard" || path === "/admin-dashboard";
  setNavItemActive(navDashboard, onDashboard);
}

function updateRoleUI(user) {
  const role = user && user.role ? user.role : "guest";
  currentUserRole = role;

  const navRole = document.getElementById("navRole");
  if (navRole) {
    navRole.textContent = `${t("nav_role_prefix")} ${roleLabel(role)}`;
  }

  const navDashboard = document.getElementById("navDashboard");
  if (navDashboard) {
    if (role === "admin" || role === "supplier") {
      navDashboard.href = dashboardPathForRole(role);
      navDashboard.textContent =
        role === "admin" ? t("nav_dashboard_admin") : t("nav_dashboard_supplier");
      navDashboard.classList.remove("hidden");
    } else {
      navDashboard.classList.add("hidden");
    }
  }

  const navLogin = document.getElementById("navLogin");
  const navRegister = document.getElementById("navRegister");
  const navProfile = document.getElementById("navProfile");
  const navLogout = document.getElementById("navLogout");
  const isAuthenticated = role !== "guest";

  if (navLogin) {
    navLogin.classList.toggle("hidden", isAuthenticated);
  }
  if (navRegister) {
    navRegister.classList.toggle("hidden", isAuthenticated);
  }
  if (navProfile) {
    navProfile.classList.toggle("hidden", !isAuthenticated);
  }
  if (navLogout) {
    navLogout.classList.toggle("hidden", !isAuthenticated);
  }

  updateNavActiveState();
}

function setCurrentUserDisplayName(name) {
  const userName = document.getElementById("currentUserName");
  if (userName) {
    userName.textContent = name;
  }
}

function resetAuthState() {
  localStorage.removeItem("access_token");
  updateRoleUI(null);
  setCurrentUserDisplayName(roleLabel("guest"));
}

function handleUnauthorizedResult(out, outputId) {
  if (out.status !== 401) {
    return false;
  }
  resetAuthState();
  setText(outputId, t("auth_session_expired"));
  window.location.href = "/login";
  return true;
}

function requireRole(requiredRole, outputId, messageKey) {
  if (currentUserRole !== requiredRole) {
    setText(outputId, t(messageKey));
    return false;
  }
  return true;
}

function requireAnyRole(allowedRoles, outputId, messageKey) {
  if (!allowedRoles.includes(currentUserRole)) {
    setText(outputId, t(messageKey));
    return false;
  }
  return true;
}

function logoutUser() {
  closeProfilePanel();
  resetAuthState();
  if (window.location.pathname === "/admin-dashboard" || window.location.pathname === "/supplier-dashboard") {
    window.location.href = "/login";
    return;
  }
  window.location.href = "/";
}

async function refreshCurrentUser() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    updateRoleUI(null);
    setCurrentUserDisplayName(roleLabel("guest"));
    return null;
  }

  const out = await requestJSON("/api/users/me");
  if (out.status !== 200) {
    resetAuthState();
    return null;
  }

  updateRoleUI(out.data);
  setCurrentUserDisplayName(out.data.name);
  return out.data;
}

async function loadMyProfile() {
  const out = await requestJSON("/api/users/me");
  if (handleUnauthorizedResult(out, "profileResult")) return;
  if (out.status !== 200) {
    setJSON("profileResult", out);
    return;
  }

  const nameInput = document.getElementById("profileName");
  const emailInput = document.getElementById("profileEmail");
  const passwordInput = document.getElementById("profilePassword");

  if (nameInput) nameInput.value = out.data.name || "";
  if (emailInput) emailInput.value = out.data.email || "";
  if (passwordInput) passwordInput.value = "";
}

function openProfilePanel() {
  if (currentUserRole === "guest" || !localStorage.getItem("access_token")) {
    window.location.href = "/login";
    return;
  }
  const panel = document.getElementById("profilePanel");
  if (!panel) return;
  panel.classList.remove("hidden");
  loadMyProfile();
}

function closeProfilePanel() {
  const panel = document.getElementById("profilePanel");
  if (!panel) return;
  panel.classList.add("hidden");
}

async function saveMyProfile() {
  const nameInput = document.getElementById("profileName");
  const emailInput = document.getElementById("profileEmail");
  const passwordInput = document.getElementById("profilePassword");
  if (!nameInput || !emailInput || !passwordInput) return;

  const payload = {};
  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (name) payload.name = name;
  if (email) payload.email = email;
  if (password.trim()) payload.password = password;

  if (Object.keys(payload).length === 0) {
    setText("profileResult", t("error_profile_fields_required"));
    return;
  }

  let out = await requestJSON("/api/users/me", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (out.status === 404) {
    out = await requestJSON("/api/users/me/update", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
  if (handleUnauthorizedResult(out, "profileResult")) return;
  setJSON("profileResult", out);

  if (out.status === 200) {
    await refreshCurrentUser();
    passwordInput.value = "";
  }
}

async function registerUser() {
  const payload = {
    name: document.getElementById("regName").value,
    email: document.getElementById("regEmail").value,
    password: document.getElementById("regPassword").value,
    role: document.getElementById("regRole").value,
  };
  const out = await requestJSON("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setJSON("registerResult", out);
}

async function loginUser() {
  const payload = {
    email: document.getElementById("loginEmail").value,
    password: document.getElementById("loginPassword").value,
  };
  const out = await requestJSON("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (out.data.access_token) {
    localStorage.setItem("access_token", out.data.access_token);
    const currentUser = await refreshCurrentUser();
    setJSON("loginResult", out);
    if (currentUser && currentUser.role) {
      window.location.href = dashboardPathForRole(currentUser.role);
      return;
    }
  }
  setJSON("loginResult", out);
}

async function loadCategories() {
  const select = document.getElementById("categorySelect");
  if (!select) return;
  const previousSelection = select.value;

  const out = await requestJSON("/api/suppliers/categories");
  if (out.status !== 200 || !Array.isArray(out.data)) {
    return;
  }

  const options = [`<option value="">${escapeHtml(t("category_all"))}</option>`];
  out.data.forEach((category) => {
    options.push(`<option value="${category.id}">${escapeHtml(category.name)}</option>`);
  });
  select.innerHTML = options.join("");

  if (previousSelection && out.data.some((category) => String(category.id) === previousSelection)) {
    select.value = previousSelection;
  }
}

function renderSuppliers(suppliers) {
  const wrap = document.getElementById("supplierCards");
  if (!wrap) return;

  if (!suppliers.length) {
    wrap.innerHTML = `<div class="rounded-2xl border border-slate-200 bg-white p-5 text-slate-600 shadow-sm">${escapeHtml(
      t("home_no_suppliers"),
    )}</div>`;
    return;
  }

  wrap.innerHTML = suppliers
    .map(
      (supplier) => `
      <article class="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
        <div class="mb-3 flex items-start justify-between gap-2">
          <div>
            <h3 class="font-display text-lg font-bold text-slate-900">${escapeHtml(supplier.business_name)}</h3>
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-brand-700">${escapeHtml(
              t("home_supplier_verified"),
            )}</p>
          </div>
          <span class="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700">${escapeHtml(
            t("home_supplier_id_prefix"),
          )} ${supplier.id}</span>
        </div>
        <p class="text-sm text-slate-600">${escapeHtml(supplier.address)}</p>
        <p class="mt-1 text-sm font-semibold text-slate-800">${escapeHtml(
          t("home_contact_number"),
        )} <a class="text-blue-700 hover:underline" href="tel:${escapeHtml(supplier.phone)}">${escapeHtml(
          supplier.phone,
        )}</a></p>
        <p class="mt-1 text-sm text-amber-700">
          ${escapeHtml(t("home_rating_label"))} ${ratingStars(supplier.average_rating)} (${Number(
            supplier.average_rating || 0,
          ).toFixed(1)}/5, ${supplier.total_reviews || 0} ${escapeHtml(t("home_reviews_suffix"))})
        </p>
        <div class="mt-4 flex flex-wrap gap-2">
          <button onclick="callSupplier(${supplier.id})" class="rounded-xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">${escapeHtml(
            t("home_call_btn"),
          )}</button>
          <button onclick="bookViaWhatsApp(${supplier.id})" class="rounded-xl bg-green-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-green-700">${escapeHtml(
            t("home_book_whatsapp_btn"),
          )}</button>
          <button onclick="rateSupplier(${supplier.id})" class="rounded-xl bg-amber-500 px-3 py-2 text-sm font-semibold text-white transition hover:bg-amber-600">${escapeHtml(
            t("home_rate_btn"),
          )}</button>
        </div>
      </article>
    `,
    )
    .join("");
}

async function searchSuppliers() {
  const categoryId = document.getElementById("categorySelect")?.value || "";
  const searchText = document.getElementById("supplierQuery")?.value?.trim() || "";

  const params = new URLSearchParams();
  if (categoryId) {
    params.set("category_id", categoryId);
  }
  if (searchText) {
    params.set("q", searchText);
  }

  const query = params.toString();
  const out = await requestJSON(`/api/suppliers/search${query ? `?${query}` : ""}`);

  if (out.status !== 200 || !Array.isArray(out.data)) {
    setJSON("actionResult", out);
    return;
  }

  supplierCache = {};
  out.data.forEach((item) => {
    supplierCache[item.id] = item;
  });

  renderSuppliers(out.data);
}

function getBookingDescription(supplier) {
  const typed = document.getElementById("bookingDescription")?.value?.trim();
  if (typed) {
    return typed;
  }
  return formatMessage(t("default_booking_desc"), { businessName: supplier.business_name });
}

function isLikelyPhoneNumber(raw) {
  const digits = String(raw || "").replace(/\D/g, "");
  return digits.length >= 7 && digits.length <= 15;
}

async function callSupplier(supplierId) {
  const supplier = supplierCache[supplierId];
  const token = localStorage.getItem("access_token");

  if (!token) {
    if (supplier && supplier.phone) {
      setText("actionResult", formatMessage(t("action_guest_direct_call"), { phone: supplier.phone }));
      window.location.href = `tel:${supplier.phone}`;
      return;
    }
    setText("actionResult", t("action_supplier_phone_unavailable"));
    return;
  }

  const out = await requestJSON(`/api/suppliers/${supplierId}/call`, { method: "POST" });
  if (handleUnauthorizedResult(out, "actionResult")) return;
  if (out.status === 200) {
    setText(
      "actionResult",
      formatMessage(t("action_call_logged"), {
        supplierId,
        phone: out.data.phone,
      }),
    );
    return;
  }
  setJSON("actionResult", out);
}

async function bookViaWhatsApp(supplierId) {
  const supplier = supplierCache[supplierId];
  if (!supplier) {
    setText("actionResult", t("action_supplier_missing_refresh"));
    return;
  }

  const description = getBookingDescription(supplier);
  const token = localStorage.getItem("access_token");
  let out;

  if (token) {
    const payload = { supplier_id: supplierId, description };
    out = await requestJSON("/api/bookings/whatsapp", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } else {
    const guestName = window.prompt(t("prompt_guest_name"), "");
    if (guestName === null || guestName.trim().length < 2) {
      setText("actionResult", t("error_guest_name"));
      return;
    }

    const guestPhone = window.prompt(t("prompt_guest_phone"), "");
    if (guestPhone === null || !isLikelyPhoneNumber(guestPhone)) {
      setText("actionResult", t("error_guest_phone"));
      return;
    }

    const payload = {
      supplier_id: supplierId,
      description,
      guest_name: guestName.trim(),
      guest_phone: guestPhone.trim(),
    };

    out = await requestJSON("/api/bookings/guest/whatsapp", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  if (out.status !== 200) {
    if (handleUnauthorizedResult(out, "actionResult")) return;
    setJSON("actionResult", out);
    return;
  }

  setText(
    "actionResult",
    formatMessage(t("action_booking_created_whatsapp"), {
      bookingId: out.data.booking_id,
      phone: out.data.phone,
    }),
  );

  if (out.data.whatsapp_url) {
    window.open(out.data.whatsapp_url, "_blank");
  }
}

async function rateSupplier(supplierId) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    setText("actionResult", t("error_login_for_rating"));
    return;
  }

  const ratingRaw = window.prompt(t("prompt_rating"), "5");
  if (ratingRaw === null) return;

  const rating = Number(ratingRaw);
  if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
    setText("actionResult", t("error_rating_range"));
    return;
  }

  const comment = window.prompt(t("prompt_comment"), "");
  if (comment === null || comment.trim().length < 2) {
    setText("actionResult", t("error_comment_min"));
    return;
  }

  const payload = { supplier_id: supplierId, rating, comment: comment.trim() };
  const out = await requestJSON(`/api/suppliers/${supplierId}/reviews`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (out.status !== 200) {
    if (handleUnauthorizedResult(out, "actionResult")) return;
    setJSON("actionResult", out);
    return;
  }

  setText("actionResult", formatMessage(t("action_rating_saved"), { supplierId }));
  await searchSuppliers();
}

async function saveSupplierProfile() {
  if (!requireAnyRole(["supplier", "admin"], "supplierResult", "supplier_auth_required")) return;
  const payload = {
    business_name: document.getElementById("spBusiness").value,
    phone: document.getElementById("spPhone").value,
    address: document.getElementById("spAddress").value,
  };
  const out = await requestJSON("/api/suppliers/profile", { method: "POST", body: JSON.stringify(payload) });
  if (handleUnauthorizedResult(out, "supplierResult")) return;
  if (out.status === 200 && out.data && typeof out.data.id === "number") {
    setText(
      "supplierResult",
      formatMessage(t("supplier_profile_saved_with_id"), { supplierId: out.data.id }),
    );
    return;
  }
  setJSON("supplierResult", out);
}

async function addSupplierService() {
  if (!requireAnyRole(["supplier", "admin"], "supplierResult", "supplier_auth_required")) return;
  const payload = {
    category_id: Number(document.getElementById("svcCategoryId").value),
    price: Number(document.getElementById("svcPrice").value),
    availability: document.getElementById("svcAvailability").value,
  };
  const out = await requestJSON("/api/suppliers/services", { method: "POST", body: JSON.stringify(payload) });
  if (handleUnauthorizedResult(out, "supplierResult")) return;
  setJSON("supplierResult", out);
}

async function loadSupplierBookings() {
  if (!requireAnyRole(["supplier", "admin"], "supplierBookings", "supplier_auth_required")) return;
  const out = await requestJSON("/api/suppliers/me/bookings");
  if (handleUnauthorizedResult(out, "supplierBookings")) return;
  setJSON("supplierBookings", out);
}

async function loadMySupplierProfiles() {
  if (!requireAnyRole(["supplier", "admin"], "supplierManageOutput", "supplier_auth_required")) return;
  const out = await requestJSON("/api/suppliers/me/profiles");
  if (handleUnauthorizedResult(out, "supplierManageOutput")) return;
  setJSON("supplierManageOutput", out);
}

async function updateSupplierProfileById() {
  if (!requireAnyRole(["supplier", "admin"], "supplierManageOutput", "supplier_auth_required")) return;

  const supplierId = Number(document.getElementById("editSupplierId")?.value);
  const businessName = document.getElementById("editSpBusiness")?.value.trim() || "";
  const phone = document.getElementById("editSpPhone")?.value.trim() || "";
  const address = document.getElementById("editSpAddress")?.value.trim() || "";

  if (!supplierId) {
    setText("supplierManageOutput", t("error_supplier_id_required"));
    return;
  }
  if (!businessName || !phone || !address) {
    setText("supplierManageOutput", t("error_supplier_profile_fields_required"));
    return;
  }

  const out = await requestJSON(`/api/suppliers/profiles/${supplierId}`, {
    method: "PUT",
    body: JSON.stringify({
      business_name: businessName,
      phone,
      address,
    }),
  });
  if (handleUnauthorizedResult(out, "supplierManageOutput")) return;
  setJSON("supplierManageOutput", out);
}

async function loadMySupplierServices() {
  if (!requireAnyRole(["supplier", "admin"], "supplierManageOutput", "supplier_auth_required")) return;
  const out = await requestJSON("/api/suppliers/me/services");
  if (handleUnauthorizedResult(out, "supplierManageOutput")) return;
  setJSON("supplierManageOutput", out);
}

async function updateSupplierServiceById() {
  if (!requireAnyRole(["supplier", "admin"], "supplierManageOutput", "supplier_auth_required")) return;

  const serviceId = Number(document.getElementById("editServiceId")?.value);
  const categoryRaw = document.getElementById("editSvcCategoryId")?.value.trim() || "";
  const priceRaw = document.getElementById("editSvcPrice")?.value.trim() || "";
  const availability = document.getElementById("editSvcAvailability")?.value.trim() || "";

  if (!serviceId) {
    setText("supplierManageOutput", t("error_service_id_required"));
    return;
  }

  const payload = {};
  if (categoryRaw) {
    const categoryId = Number(categoryRaw);
    if (!Number.isFinite(categoryId) || categoryId <= 0) {
      setText("supplierManageOutput", t("error_invalid_category_id"));
      return;
    }
    payload.category_id = categoryId;
  }
  if (priceRaw) {
    const price = Number(priceRaw);
    if (!Number.isFinite(price) || price <= 0) {
      setText("supplierManageOutput", t("error_invalid_price"));
      return;
    }
    payload.price = price;
  }
  if (availability) payload.availability = availability;

  if (Object.keys(payload).length === 0) {
    setText("supplierManageOutput", t("error_supplier_service_update_fields_required"));
    return;
  }

  const out = await requestJSON(`/api/suppliers/services/${serviceId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (handleUnauthorizedResult(out, "supplierManageOutput")) return;
  setJSON("supplierManageOutput", out);
}

async function approveSupplier() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const supplierId = Number(document.getElementById("approveSupplierId").value);
  if (!supplierId) {
    setText("adminOutput", t("error_supplier_id_required"));
    return;
  }
  const out = await requestJSON(`/api/admin/suppliers/${supplierId}/approve`, { method: "POST" });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function blockSupplier() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const supplierId = Number(document.getElementById("blockSupplierId").value);
  if (!supplierId) {
    setText("adminOutput", t("error_supplier_id_required"));
    return;
  }
  const out = await requestJSON(`/api/admin/suppliers/${supplierId}/block`, { method: "POST" });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function unblockSupplier() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const supplierId = Number(document.getElementById("blockSupplierId").value);
  if (!supplierId) {
    setText("adminOutput", t("error_supplier_id_required"));
    return;
  }
  const out = await requestJSON(`/api/admin/suppliers/${supplierId}/unblock`, { method: "POST" });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function deleteSupplierById() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const supplierId = Number(document.getElementById("deleteSupplierId").value);
  if (!supplierId) {
    setText("adminOutput", t("error_supplier_id_required"));
    return;
  }
  if (!window.confirm(t("admin_delete_supplier_confirm"))) return;

  const out = await requestJSON(`/api/admin/suppliers/${supplierId}`, { method: "DELETE" });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function deleteUserById() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const userId = Number(document.getElementById("deleteUserId").value);
  if (!userId) {
    setText("adminOutput", t("error_user_id_required"));
    return;
  }
  if (!window.confirm(t("admin_delete_user_confirm"))) return;

  const out = await requestJSON(`/api/admin/users/${userId}`, { method: "DELETE" });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function createCategory() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const categoryName = document.getElementById("newCategoryName").value.trim();
  if (!categoryName) {
    setText("adminOutput", t("error_category_name_required"));
    return;
  }
  const payload = { name: categoryName };
  const out = await requestJSON("/api/admin/categories", { method: "POST", body: JSON.stringify(payload) });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function loadPendingSuppliers() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const out = await requestJSON("/api/admin/pending-suppliers");
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  if (out.status === 200 && Array.isArray(out.data)) {
    if (out.data.length === 0) {
      setText("adminOutput", t("admin_pending_empty"));
      return;
    }
    const lines = [t("admin_pending_hint"), ""];
    out.data.forEach((supplier) => {
      lines.push(
        formatMessage(t("admin_pending_item"), {
          supplierId: supplier.id,
          businessName: supplier.business_name,
          phone: supplier.phone,
        }),
      );
    });
    setText("adminOutput", lines.join("\n"));
    return;
  }
  setJSON("adminOutput", out);
}

async function loadAllBookings() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const out = await requestJSON("/api/admin/bookings");
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

document.addEventListener("DOMContentLoaded", async () => {
  initLanguageToggle();
  const currentUser = await refreshCurrentUser();
  enforcePageAccess(currentUser);
  await loadCategories();

  if (document.getElementById("supplierCards")) {
    await searchSuppliers();
  }
});
