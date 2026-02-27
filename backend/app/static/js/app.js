let supplierCache = {};
let currentUserRole = "guest";
let isProfilePanelOpen = false;
let categoryNameById = {};
let categoryList = [];
let homeCategoryItems = [];
let lastRenderedSearchSuppliers = [];
let activeSupplierProfileId = null;
let siteSettings = {
  show_supplier_phone: true,
  enable_supplier_call: true,
  enable_supplier_whatsapp: true,
};

const UI_LANG_STORAGE_KEY = "ui_lang_mode";

const CATEGORY_UI_CONFIG = {
  building_material: { icon: "fa-solid fa-trowel-bricks" },
  vehicle_booking: { icon: "fa-solid fa-truck-fast" },
  agriculture_supplies: { icon: "fa-solid fa-seedling" },
  equipment_rental: { icon: "fa-solid fa-screwdriver-wrench" },
  local_services: { icon: "fa-solid fa-handshake-angle" },
};

const uiText = {
  hinglish: {
    nav_home: "होम",
    nav_login: "लॉगिन",
    nav_register: "रजिस्टर करें",
    nav_profile: "प्रोफाइल",
    nav_logout: "लॉगआउट",
    nav_role_prefix: "भूमिका: ",
    nav_dashboard_admin: "Admin डैशबोर्ड",
    nav_dashboard_supplier: "Supplier डैशबोर्ड",
    global_search_placeholder: "Keyword, sentence, या material नाम लिखें",
    global_search_btn: "Search",
    global_voice_btn: "Voice",
    global_tags_label: "Quick tags:",
    global_search_empty: "कृपया keyword या sentence लिखें।",
    global_search_running: "Searching: {query}",
    global_search_redirect: "Search खुल रहा है...",
    global_voice_listening: "Listening... बोलिए",
    global_voice_detected: "Detected: {query}",
    global_voice_error: "Voice input समझ नहीं आया। फिर से कोशिश करें।",
    footer_tagline: "तेज सप्लायर खोज, बुकिंग और WhatsApp कन्वर्जन के लिए बनाया गया प्लेटफॉर्म।",
    footer_privacy_note: "प्राइवेसी नोट",
    brand_network_tagline: "गांव-कस्बा सप्लायर नेटवर्क",
    top_strip_message: "भारत का गांव-केंद्रित सप्लायर और सेवा नेटवर्क",
    top_strip_email: "सपोर्ट:",
    top_strip_phone: "कॉल:",

    role_guest: "मेहमान",
    role_user: "यूज़र",
    role_supplier: "सप्लायर",
    role_admin: "एडमिन",
    auth_session_expired: "सेशन समाप्त/अमान्य है। कृपया दोबारा लॉगिन करें।",
    auth_account_blocked: "आपका अकाउंट एडमिन द्वारा ब्लॉक किया गया है।",
    buyer_action_only: "यह क्रिया केवल Buyer/User या Admin के लिए उपलब्ध है।",
    admin_phone_not_allowed: "Admin लॉगिन के लिए allowlisted नंबर उपयोग करें।",
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
    error_supplier_service_update_fields_required:
      "सेवा अपडेट के लिए कम से कम एक फ़ील्ड दें (item/category/price/availability/photo)।",
    error_item_name_or_details_required: "कृपया item name भरें।",

    home_badge: "भरोसेमंद ग्रामीण मार्केटप्लेस",
    home_title: "अब गांव से ही सप्लायर, वाहन और रेंटल सेवा तुरंत बुक करें",
    home_desc:
      "GraminHub पर Book Vehicle, Building Materials और Agriculture सेवाएं एक ही जगह मिलती हैं।",
    home_logged_in_as: "लॉगिन यूज़र:",
    home_booking_mode: "बुकिंग: Call + WhatsApp",
    home_verified_chip: "Verified local network",
    home_search_title: "तुरंत खोजें और बुक करें",
    home_search_desc:
      "Category चुनें, अपनी जरूरत लिखें, सप्लायर खोजें और WhatsApp से बुकिंग शुरू करें।",
    home_category_label: "श्रेणी चुनें",
    home_query_label: "सप्लायर खोजें (नाम/स्थान/मोबाइल)",
    home_query_placeholder: "उदाहरण: Sonbhadra, JCB, 98765...",
    home_keyword_label: "Simple keyword search",
    home_keyword_placeholder: "जैसे: cement, heavy, request",
    home_keyword_btn: "Keyword Search",
    home_keyword_required: "Keyword search के लिए कम से कम एक keyword लिखें।",
    home_voice_btn: "Voice",
    home_voice_hint: "Voice button से keyword बोलकर भी खोज सकते हैं (browser support पर निर्भर)।",
    home_voice_not_supported: "आपके browser में voice search support नहीं है।",
    home_voice_start: "Voice सुनना शुरू... keyword बोलें।",
    home_voice_no_result: "Voice से कोई शब्द नहीं मिला। फिर से प्रयास करें।",
    home_guest_name_placeholder: "Guest नाम (optional)",
    home_guest_phone_placeholder: "Guest मोबाइल (optional)",
    home_requirement_label: "आपको क्या चाहिए",
    home_requirement_placeholder: "उदाहरण: सोनभद्र में 2 दिन के लिए ट्रैक्टर ट्रॉली चाहिए",
    home_search_btn: "सप्लायर खोजें",
    home_search_result_count: "खोज परिणाम: {count} सप्लायर मिले।",
    home_booking_note_prefix:
      "आप बिना लॉगिन भी बुकिंग कर सकते हैं (नाम + मोबाइल देकर)। लॉगिन करने पर",
    home_booking_note_suffix: "भूमिका से और बेहतर ट्रैकिंग मिलेगी।",
    home_available_title: "उपलब्ध सप्लायर",
    home_available_desc: "सीधा फोन करने के लिए Call दबाएं या WhatsApp से बुकिंग शुरू करें।",
    home_results_title: "Searched Suppliers / Items",
    home_results_desc: "Keyword या Voice search के बाद relevant suppliers यहां ऊपर दिखेंगे।",
    home_search_prompt: "ऊपर search box से keyword/voice search करें, तब results यहां दिखेंगे।",
    home_three_col_title: "Top Categories",
    home_three_col_desc: "हर category के top 2-3 items यहां default दिखते हैं।",
    home_col_vehicle_title: "Book Vehicle",
    home_col_vehicle_desc: "Car, Truck, Auto, Tractor जैसे options.",
    home_col_material_title: "Buy Building Materials",
    home_col_material_desc: "Cement, Sand, Balu, Steel जैसे items.",
    home_col_agri_title: "Agriculture",
    home_col_agri_desc: "Seeds, Fertilizer, Pesticide, Farm tools.",
    home_col_sort_label: "Subcategory filter",
    home_col_empty: "इस फिल्टर में अभी item उपलब्ध नहीं है।",
    home_col_error: "Category items अभी लोड नहीं हो पाए।",
    home_filter_all: "All",
    home_filter_car: "Car",
    home_filter_truck: "Truck",
    home_filter_auto: "Auto",
    home_filter_tractor: "Tractor",
    home_filter_jcb: "JCB/Crane",
    home_filter_cement: "Cement",
    home_filter_sand: "Sand/Balu",
    home_filter_steel: "Steel",
    home_filter_brick: "Bricks",
    home_filter_seed: "Seeds",
    home_filter_fertilizer: "Fertilizer",
    home_filter_pesticide: "Pesticide",
    home_filter_tool: "Farm Tools",
    home_disclaimer_title: "Important Disclaimer",
    home_disclaimer_desc: "User, Buyer और Supplier सभी के लिए safety और fraud-control disclaimers लागू हैं।",
    home_disclaimer_btn: "View Full Disclaimer",
    home_console_title: "लाइव एक्टिविटी कंसोल",
    home_console_desc: "खोज, कॉल और बुकिंग के दौरान API रिस्पॉन्स ऊपर results card में दिखेगा।",
    home_owner_title: "ओनर/सपोर्ट संपर्क",
    home_owner_desc: "कोई समस्या हो तो सीधे संपर्क करें:",
    home_owner_email: "ईमेल:",
    home_owner_whatsapp: "WhatsApp:",

    home_feature_category_label: "श्रेणी",
    home_feature_materials_desc: "सीमेंट, गिट्टी, बालू, स्टील और साइट का पूरा सामान।",
    home_feature_vehicle_desc: "Truck, Car, Auto, Tractor जैसी वाहन बुकिंग।",
    home_feature_agri_desc: "बीज, खाद, कीटनाशक और खेती से जुड़े सामान व सेवाएं।",
    home_feature_heavy_desc: "JCB, Excavator, Loader जैसी भारी मशीनरी बुकिंग।",
    home_feature_transport_desc: "Truck, mini-truck और स्थानीय लॉजिस्टिक्स सपोर्ट।",
    home_feature_rental_desc: "छोटे और लंबे समय के लिए उपकरण किराये पर।",
    home_tags_title: "लोकप्रिय खोज टैग",
    home_tags_desc: "एक टैग पर क्लिक करें और तुरंत सप्लायर सूची देखें।",
    home_tab_discover: "खोज और बुकिंग",
    home_tab_workflow: "वर्कफ्लो",
    home_tab_support: "सपोर्ट",
    home_flow_title: "कैसे काम करता है",
    home_flow_desc: "3 आसान स्टेप में खोज से बुकिंग तक पूरा workflow।",
    home_flow_step_1_title: "श्रेणी चुनें",
    home_flow_step_1_desc: "सामग्री, वाहन या उपकरण जैसी category चुनें।",
    home_flow_step_2_title: "Verified सप्लायर देखें",
    home_flow_step_2_desc: "रेटिंग और संपर्क नंबर के साथ लिस्टिंग देखें।",
    home_flow_step_3_title: "Call या WhatsApp से बुक करें",
    home_flow_step_3_desc: "रिक्वेस्ट भेजें और तुरंत सप्लायर से बात करें।",
    home_support_title: "ओनर/सपोर्ट संपर्क",
    home_support_desc: "कोई समस्या हो तो सीधे संपर्क करें:",
    home_support_note: "लोकल टेस्ट के लिए पहले demo data seed करें, फिर demo phone numbers से OTP लॉगिन करें।",

    category_all: "सभी श्रेणियां",
    home_no_suppliers: "इस श्रेणी में अभी कोई approved सप्लायर नहीं मिला।",
    home_supplier_verified: "Verified सप्लायर",
    home_supplier_id_prefix: "आईडी",
    home_item_label: "आइटम:",
    home_supplier_details_label: "सप्लायर विवरण",
    home_item_variant_label: "वैरायटी:",
    home_item_details_label: "विवरण:",
    home_item_price_label: "कीमत:",
    home_item_availability_label: "उपलब्धता:",
    home_item_photos_label: "फोटो:",
    home_item_not_listed: "इस सप्लायर ने अभी item list नहीं जोड़ी है।",
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
    form_title: "लॉगिन",
    form_desc: "Buyer, Supplier और Owner/Admin के लिए सिर्फ मोबाइल नंबर और OTP लॉगिन उपयोग करें।",
    otp_title: "Phone OTP Login (User/Supplier/Admin)",
    otp_desc: "Email की जरूरत नहीं। फोन नंबर डालें, OTP लें और लॉगिन करें।",
    otp_admin_note: "Owner/Admin लॉगिन सिर्फ allowlisted नंबरों पर सक्षम है।",
    otp_phone_placeholder: "फोन नंबर",
    otp_role_user: "Buyer/User",
    otp_role_supplier: "Supplier",
    otp_role_admin: "Owner/Admin",
    otp_request_btn: "Get OTP",
    otp_code_placeholder: "Enter OTP",
    otp_verify_btn: "Verify OTP & Login",
    otp_hint: "Demo OTP स्क्रीन पर दिखेगा।",
    otp_phone_required: "कृपया सही फोन नंबर दर्ज करें।",
    otp_code_required: "कृपया OTP दर्ज करें।",
    otp_requested: "OTP भेजा गया। Demo OTP: {otp}",
    token_note: "इस MVP डेमो में टोकन localStorage में सेव होता है।",
    login_demo_title: "लोकल डेमो लॉगिन",
    login_demo_desc: "make demo-ready के बाद इन मोबाइल नंबरों से OTP टेस्ट करें:",
    login_demo_admin: "Admin: 9000000001",
    login_demo_user: "Buyer/User: 9000000002",
    login_demo_supplier_1: "Supplier 1: 9000000003",
    login_demo_supplier_2: "Supplier 2: 9000000004",
    login_demo_password_hint: "OTP request response में demo OTP दिखता है।",
    result_waiting: "प्रतीक्षा...",
    no_account: "अकाउंट नहीं है?",
    register_now: "रजिस्टर करें",

    register_title: "रजिस्टर करें",
    register_desc: "रजिस्टर करके सप्लायर खोजें और बुकिंग करें।",
    register_name_label: "पूरा नाम",
    register_name_placeholder: "अपना पूरा नाम लिखें",
    register_email_label: "ईमेल",
    register_email_placeholder: "name@example.com",
    register_phone_label: "मोबाइल नंबर",
    register_phone_placeholder: "10-digit mobile number",
    register_password_label: "पासवर्ड",
    register_password_placeholder: "नया पासवर्ड बनाएं",
    register_role_label: "भूमिका (Role)",
    register_role_user: "User (ग्राहक)",
    register_role_supplier: "Supplier (विक्रेता)",
    register_role_admin: "Admin (प्रशासन)",
    register_phone_required: "रजिस्ट्रेशन के लिए मोबाइल नंबर जरूरी है।",
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
    register_panel_note_title: "Note",
    register_panel_note_desc: "Public registration में Buyer/User और Supplier roles ही दिखाए जाते हैं।",

    profile_title: "प्रोफाइल सेटिंग्स",
    profile_desc: "नाम, ईमेल और पासवर्ड अपडेट करें। यह विकल्प User, Supplier और Admin सभी के लिए है।",
    profile_name_label: "नाम",
    profile_name_placeholder: "अपना नाम",
    profile_email_label: "ईमेल",
    profile_email_placeholder: "name@example.com",
    profile_phone_label: "मोबाइल नंबर",
    profile_phone_placeholder: "10-digit mobile number",
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
    supplier_service_desc: "Item name/details/variant और 2-3 फोटो जोड़ें ताकि यूज़र आपकी लिस्टिंग साफ देखें।",
    supplier_service_category_placeholder: "Category ID (जैसे 2)",
    supplier_service_item_name_placeholder: "आइटम नाम (जैसे PPC Cement)",
    supplier_service_item_variant_placeholder: "वैरायटी / ग्रेड (जैसे 50kg bag)",
    supplier_service_item_details_placeholder: "आइटम विवरण (optional)",
    supplier_service_price_placeholder: "कीमत",
    supplier_service_availability_placeholder: "उपलब्धता (available/on request)",
    supplier_service_photo_1_placeholder: "Photo URL 1",
    supplier_service_photo_2_placeholder: "Photo URL 2 (optional)",
    supplier_service_photo_3_placeholder: "Photo URL 3 (optional)",
    supplier_service_add_btn: "सेवा जोड़ें",
    supplier_manage_title: "जुड़े हुए रिकॉर्ड एडिट करें",
    supplier_manage_desc: "अपने पुराने Supplier प्रोफाइल और जोड़ी गई सेवाएं ID से अपडेट करें।",
    supplier_manage_load_profiles_btn: "मेरे प्रोफाइल लोड करें",
    supplier_manage_supplier_id_placeholder: "Supplier ID",
    supplier_manage_update_profile_btn: "Supplier प्रोफाइल अपडेट करें",
    supplier_manage_load_services_btn: "मेरी सेवाएं लोड करें",
    supplier_manage_service_id_placeholder: "Service ID",
    supplier_manage_update_service_btn: "सेवा अपडेट करें",
    supplier_manage_delete_service_btn: "सेवा हटाएं",
    supplier_activity_title: "Supplier गतिविधि",
    supplier_activity_desc: "प्रोफाइल/सेवा अपडेट का API रिस्पॉन्स यहां देखें।",
    supplier_activity_waiting: "रिस्पॉन्स यहां दिखेगा...",
    supplier_incoming_title: "आने वाली बुकिंग रिक्वेस्ट",
    supplier_incoming_desc: "यूज़र्स की नई बुकिंग रिक्वेस्ट यहां देखें।",
    supplier_refresh_btn: "रिफ्रेश",
    supplier_tab_setup: "Setup",
    supplier_tab_manage: "Manage Records",
    supplier_tab_bookings: "Bookings",
    supplier_manage_tab_profiles: "Supplier Profiles",
    supplier_manage_tab_services: "Supplier Services",

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
    admin_tab_operations: "Supplier Ops",
    admin_tab_configuration: "Configuration",
    admin_tab_data: "Data & Moderation",
    admin_data_tab_pending: "Pending Suppliers",
    admin_data_tab_bookings: "All Bookings",
    admin_data_tab_delete: "Delete IDs",
  },
  english: {
    nav_home: "Home",
    nav_login: "Login",
    nav_register: "Register",
    nav_profile: "Profile",
    nav_logout: "Logout",
    nav_role_prefix: "Role: ",
    nav_dashboard_admin: "Admin Dashboard",
    nav_dashboard_supplier: "Supplier Dashboard",
    global_search_placeholder: "Type keyword, sentence, or material name",
    global_search_btn: "Search",
    global_voice_btn: "Voice",
    global_tags_label: "Quick tags:",
    global_search_empty: "Please enter a keyword or sentence.",
    global_search_running: "Searching: {query}",
    global_search_redirect: "Opening search...",
    global_voice_listening: "Listening... speak now",
    global_voice_detected: "Detected: {query}",
    global_voice_error: "Could not understand voice input. Try again.",
    footer_tagline:
      "Built for fast supplier discovery, booking, and WhatsApp conversion.",
    footer_privacy_note: "Privacy Note",
    brand_network_tagline: "Village-Town Supplier Network",
    top_strip_message: "India's village-first supplier and services network",
    top_strip_email: "Support:",
    top_strip_phone: "Call:",

    role_guest: "Guest",
    role_user: "User",
    role_supplier: "Supplier",
    role_admin: "Admin",
    auth_session_expired: "Session expired or invalid. Please log in again.",
    auth_account_blocked: "Your account is blocked by admin.",
    buyer_action_only: "This action is available only for Buyer/User or Admin.",
    admin_phone_not_allowed: "Use an allowlisted phone number for Admin login.",
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
    error_supplier_service_update_fields_required:
      "Provide at least one field (item/category/price/availability/photo).",
    error_item_name_or_details_required: "Item name is required.",

    home_badge: "Verified Rural Marketplace",
    home_title: "Find trusted local suppliers and book vehicles nearby",
    home_desc:
      "GraminHub helps you discover building materials and vehicle services from verified local suppliers. More categories are coming soon.",
    home_logged_in_as: "Logged in user:",
    home_booking_mode: "Booking: Call + WhatsApp",
    home_verified_chip: "Verified local network",
    home_search_title: "Search and Book Instantly",
    home_search_desc:
      "Select category, write your requirement, find suppliers, and start booking on WhatsApp.",
    home_category_label: "Category",
    home_query_label: "Search supplier (name/location/mobile)",
    home_query_placeholder: "Example: Sonbhadra, JCB, 98765...",
    home_keyword_label: "Simple keyword search",
    home_keyword_placeholder: "Example: cement, heavy, request",
    home_keyword_btn: "Keyword Search",
    home_keyword_required: "Enter at least one keyword for keyword search.",
    home_voice_btn: "Voice",
    home_voice_hint: "Use voice button to speak keyword (browser support required).",
    home_voice_not_supported: "Voice search is not supported in this browser.",
    home_voice_start: "Listening... please speak keyword.",
    home_voice_no_result: "No voice keyword detected. Please try again.",
    home_guest_name_placeholder: "Guest name (optional)",
    home_guest_phone_placeholder: "Guest mobile (optional)",
    home_requirement_label: "Your Requirement",
    home_requirement_placeholder: "Example: Need tractor with trolley for 2 days in Sonbhadra",
    home_search_btn: "Search Suppliers",
    home_search_result_count: "Search result: {count} suppliers found.",
    home_booking_note_prefix:
      "You can also book without login (with name + mobile). With login as",
    home_booking_note_suffix: "role, tracking is better.",
    home_available_title: "Available Suppliers",
    home_available_desc: "Tap Call for direct contact or WhatsApp to start booking.",
    home_results_title: "Searched Suppliers / Items",
    home_results_desc: "After keyword or voice search, relevant suppliers appear here at the top.",
    home_search_prompt: "Use the top search box (keyword/voice) to show matching results here.",
    home_three_col_title: "Top Categories",
    home_three_col_desc: "By default, top 2-3 items are shown for each category.",
    home_col_vehicle_title: "Book Vehicle",
    home_col_vehicle_desc: "Car, Truck, Auto, Tractor options.",
    home_col_material_title: "Buy Building Materials",
    home_col_material_desc: "Cement, Sand, Balu, Steel items.",
    home_col_agri_title: "Agriculture",
    home_col_agri_desc: "Seeds, Fertilizer, Pesticide, Farm tools.",
    home_col_sort_label: "Subcategory filter",
    home_col_empty: "No items found for this filter yet.",
    home_col_error: "Could not load category items right now.",
    home_filter_all: "All",
    home_filter_car: "Car",
    home_filter_truck: "Truck",
    home_filter_auto: "Auto",
    home_filter_tractor: "Tractor",
    home_filter_jcb: "JCB/Crane",
    home_filter_cement: "Cement",
    home_filter_sand: "Sand/Balu",
    home_filter_steel: "Steel",
    home_filter_brick: "Bricks",
    home_filter_seed: "Seeds",
    home_filter_fertilizer: "Fertilizer",
    home_filter_pesticide: "Pesticide",
    home_filter_tool: "Farm Tools",
    home_disclaimer_title: "Important Disclaimer",
    home_disclaimer_desc: "Safety and fraud-control disclaimers apply for User, Buyer, and Supplier flows.",
    home_disclaimer_btn: "View Full Disclaimer",
    home_console_title: "Live Activity Console",
    home_console_desc: "API responses appear in the top results card while searching, calling, and booking.",
    home_owner_title: "Owner/Support Contact",
    home_owner_desc: "For any issue, contact directly:",
    home_owner_email: "Email:",
    home_owner_whatsapp: "WhatsApp:",

    home_feature_category_label: "Category",
    home_feature_materials_desc: "Cement, aggregate, sand, steel, and complete site materials.",
    home_feature_vehicle_desc: "Vehicle booking for truck, car, auto, and tractor.",
    home_feature_agri_desc: "Seeds, fertilizer, pesticide, and farm-related goods/services.",
    home_feature_heavy_desc: "Book heavy machinery like JCB, Excavator, and Loader.",
    home_feature_transport_desc: "Truck, mini-truck, and local logistics support.",
    home_feature_rental_desc: "Equipment rentals for short and long durations.",
    home_tags_title: "Popular Search Tags",
    home_tags_desc: "Click a tag and instantly load matching suppliers.",
    home_tab_discover: "Discover & Book",
    home_tab_workflow: "Workflow",
    home_tab_support: "Support",
    home_flow_title: "How It Works",
    home_flow_desc: "From discovery to booking in 3 clear steps.",
    home_flow_step_1_title: "Pick a Category",
    home_flow_step_1_desc: "Choose materials, vehicles, or equipment rentals.",
    home_flow_step_2_title: "Review Verified Suppliers",
    home_flow_step_2_desc: "Compare listings with ratings and contact details.",
    home_flow_step_3_title: "Book via Call or WhatsApp",
    home_flow_step_3_desc: "Send your requirement and connect instantly.",
    home_support_title: "Owner/Support Contact",
    home_support_desc: "For any issue, contact directly:",
    home_support_note: "For local testing, seed demo data first and then use demo phone numbers with OTP login.",

    category_all: "All Categories",
    home_no_suppliers: "No approved suppliers found in this category yet.",
    home_supplier_verified: "Verified Supplier",
    home_supplier_id_prefix: "ID",
    home_item_label: "Item:",
    home_supplier_details_label: "Supplier Details",
    home_item_variant_label: "Variant:",
    home_item_details_label: "Details:",
    home_item_price_label: "Price:",
    home_item_availability_label: "Availability:",
    home_item_photos_label: "Photos:",
    home_item_not_listed: "No item list added by this supplier yet.",
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
    form_title: "Login",
    form_desc: "Use phone number + OTP for Buyer, Supplier, and Owner/Admin login.",
    otp_title: "Phone OTP Login (User/Supplier/Admin)",
    otp_desc: "No email needed. Enter phone, get an OTP, and log in.",
    otp_admin_note: "Owner/Admin login works only for allowlisted phone numbers.",
    otp_phone_placeholder: "Phone number",
    otp_role_user: "Buyer/User",
    otp_role_supplier: "Supplier",
    otp_role_admin: "Owner/Admin",
    otp_request_btn: "Get OTP",
    otp_code_placeholder: "Enter OTP",
    otp_verify_btn: "Verify OTP & Login",
    otp_hint: "Demo OTP appears on screen.",
    otp_phone_required: "Please enter a valid phone number.",
    otp_code_required: "Please enter OTP.",
    otp_requested: "OTP issued. Demo OTP: {otp}",
    token_note: "For this MVP demo, the token is stored in localStorage.",
    login_demo_title: "Local Demo Login",
    login_demo_desc: "Test OTP with these phone numbers after running make demo-ready:",
    login_demo_admin: "Admin: 9000000001",
    login_demo_user: "Buyer/User: 9000000002",
    login_demo_supplier_1: "Supplier 1: 9000000003",
    login_demo_supplier_2: "Supplier 2: 9000000004",
    login_demo_password_hint: "Demo OTP is shown in the OTP request response.",
    result_waiting: "Waiting...",
    no_account: "No account?",
    register_now: "Register now",

    register_title: "Create a New Account",
    register_desc: "Register once and start supplier search and booking.",
    register_name_label: "Full Name",
    register_name_placeholder: "Enter your full name",
    register_email_label: "Email",
    register_email_placeholder: "name@example.com",
    register_phone_label: "Mobile Number",
    register_phone_placeholder: "10-digit mobile number",
    register_password_label: "Password",
    register_password_placeholder: "Create a new password",
    register_role_label: "Role",
    register_role_user: "User (Buyer)",
    register_role_supplier: "Supplier (Seller)",
    register_role_admin: "Admin",
    register_phone_required: "Mobile number is required for registration.",
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
    register_panel_note_title: "Note",
    register_panel_note_desc: "Public registration shows only Buyer/User and Supplier roles.",

    profile_title: "Profile Settings",
    profile_desc: "Update your name, email, and password. Available for User, Supplier, and Admin.",
    profile_name_label: "Name",
    profile_name_placeholder: "Enter your name",
    profile_email_label: "Email",
    profile_email_placeholder: "name@example.com",
    profile_phone_label: "Mobile Number",
    profile_phone_placeholder: "10-digit mobile number",
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
    supplier_service_desc: "Add item name/details/variant with up to 3 photos for clear user visibility.",
    supplier_service_category_placeholder: "Category ID (e.g. 2)",
    supplier_service_item_name_placeholder: "Item name (e.g. PPC Cement)",
    supplier_service_item_variant_placeholder: "Variant/grade (e.g. 50kg bag)",
    supplier_service_item_details_placeholder: "Item details (optional)",
    supplier_service_price_placeholder: "Price",
    supplier_service_availability_placeholder: "Availability (available/on request)",
    supplier_service_photo_1_placeholder: "Photo URL 1",
    supplier_service_photo_2_placeholder: "Photo URL 2 (optional)",
    supplier_service_photo_3_placeholder: "Photo URL 3 (optional)",
    supplier_service_add_btn: "Add Service",
    supplier_manage_title: "Edit Existing Records",
    supplier_manage_desc: "Update your existing supplier profiles and added services by ID.",
    supplier_manage_load_profiles_btn: "Load My Profiles",
    supplier_manage_supplier_id_placeholder: "Supplier ID",
    supplier_manage_update_profile_btn: "Update Supplier Profile",
    supplier_manage_load_services_btn: "Load My Services",
    supplier_manage_service_id_placeholder: "Service ID",
    supplier_manage_update_service_btn: "Update Service",
    supplier_manage_delete_service_btn: "Delete Service",
    supplier_activity_title: "Supplier Activity",
    supplier_activity_desc: "View API responses for profile/service updates here.",
    supplier_activity_waiting: "Response will appear here...",
    supplier_incoming_title: "Incoming Booking Requests",
    supplier_incoming_desc: "View fresh user booking requests here.",
    supplier_refresh_btn: "Refresh",
    supplier_tab_setup: "Setup",
    supplier_tab_manage: "Manage Records",
    supplier_tab_bookings: "Bookings",
    supplier_manage_tab_profiles: "Supplier Profiles",
    supplier_manage_tab_services: "Supplier Services",

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
    admin_tab_operations: "Supplier Ops",
    admin_tab_configuration: "Configuration",
    admin_tab_data: "Data & Moderation",
    admin_data_tab_pending: "Pending Suppliers",
    admin_data_tab_bookings: "All Bookings",
    admin_data_tab_delete: "Delete IDs",
  },
};

const HOME_CATEGORY_COLUMNS = {
  book_vehicle: {
    containerId: "homeItemsBookVehicle",
    filterId: "homeFilterBookVehicle",
    filterOptions: [
      { value: "all", labelKey: "home_filter_all", keywords: [] },
      { value: "car", labelKey: "home_filter_car", keywords: ["car", "cab", "taxi", "suv"] },
      { value: "truck", labelKey: "home_filter_truck", keywords: ["truck", "lorry", "tipper", "mini truck"] },
      { value: "auto", labelKey: "home_filter_auto", keywords: ["auto", "rickshaw", "tempo"] },
      { value: "tractor", labelKey: "home_filter_tractor", keywords: ["tractor", "trolley"] },
      { value: "jcb", labelKey: "home_filter_jcb", keywords: ["jcb", "crane", "loader", "excavator", "hydra"] },
    ],
  },
  buy_materials: {
    containerId: "homeItemsMaterials",
    filterId: "homeFilterMaterials",
    filterOptions: [
      { value: "all", labelKey: "home_filter_all", keywords: [] },
      { value: "cement", labelKey: "home_filter_cement", keywords: ["cement"] },
      { value: "sand", labelKey: "home_filter_sand", keywords: ["sand", "balu", "balu", "aggregate", "gitti"] },
      { value: "steel", labelKey: "home_filter_steel", keywords: ["steel", "rod", "tmt"] },
      { value: "brick", labelKey: "home_filter_brick", keywords: ["brick", "bricks", "tile", "tiles"] },
    ],
  },
};

const HOME_BUCKET_KEYWORDS = {
  book_vehicle: [
    "vehicle",
    "vehicles",
    "transport",
    "truck",
    "car",
    "auto",
    "tractor",
    "jcb",
    "crane",
    "loader",
    "excavator",
    "rental",
  ],
  buy_materials: [
    "construction",
    "material",
    "materials",
    "cement",
    "sand",
    "balu",
    "steel",
    "brick",
    "aggregate",
    "gitti",
  ],
};

function formatMessage(template, values = {}) {
  return Object.entries(values).reduce(
    (message, [key, value]) => message.replaceAll(`{${key}}`, String(value)),
    template,
  );
}

function normalizeText(value) {
  return String(value || "").trim().toLowerCase();
}

function textContainsAny(haystack, needles) {
  if (!haystack || !needles.length) return false;
  return needles.some((needle) => haystack.includes(needle));
}

function serviceSearchText(supplier, service) {
  const categoryName = categoryNameById[service?.category_id] || "";
  return normalizeText(
    [
      supplier?.business_name,
      supplier?.address,
      supplier?.phone,
      service?.item_name,
      service?.item_variant,
      service?.item_details,
      service?.availability,
      categoryName,
    ].join(" "),
  );
}

function inferHomeBucket(supplier, service) {
  const text = serviceSearchText(supplier, service);
  if (textContainsAny(text, HOME_BUCKET_KEYWORDS.buy_materials)) {
    return "buy_materials";
  }
  if (textContainsAny(text, HOME_BUCKET_KEYWORDS.book_vehicle)) {
    return "book_vehicle";
  }
  return "buy_materials";
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

  document.documentElement.setAttribute("data-ui-lang", normalized);
  document.documentElement.setAttribute("lang", normalized === "english" ? "en" : "hi");
  const body = document.body;
  if (body) {
    body.classList.toggle("gh-font-en", normalized === "english");
    body.classList.toggle("gh-font-hi", normalized !== "english");
  }
  localStorage.setItem(UI_LANG_STORAGE_KEY, normalized);
  setLanguageButtonState(normalized);

  updateRoleUI({ role: currentUserRole });

  if (document.getElementById("supplierCards")) {
    const emptyMessage =
      lastRenderedSearchSuppliers.length > 0 ? t("home_no_suppliers") : t("home_search_prompt");
    renderSuppliers(lastRenderedSearchSuppliers, { emptyMessage });
  }

  if (document.getElementById("homeCategoryColumns")) {
    renderHomeCategoryColumns();
  }
  loadCategories();
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

function initTabs() {
  document.querySelectorAll("[data-tab-group]").forEach((groupEl) => {
    const groupName = groupEl.getAttribute("data-tab-group");
    if (!groupName) return;

    const buttons = Array.from(groupEl.querySelectorAll(`[data-tab-button="${groupName}"]`));
    const panels = Array.from(groupEl.querySelectorAll(`[data-tab-panel="${groupName}"]`));
    if (!buttons.length || !panels.length) return;

    const activateTab = (targetId) => {
      buttons.forEach((button) => {
        const isActive = button.getAttribute("data-tab-target") === targetId;
        button.classList.toggle("gh-tab-btn-active", isActive);
        button.setAttribute("aria-selected", isActive ? "true" : "false");
      });

      panels.forEach((panel) => {
        const isActive = panel.id === targetId;
        panel.classList.toggle("hidden", !isActive);
      });
    };

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const targetId = button.getAttribute("data-tab-target");
        if (targetId) activateTab(targetId);
      });
    });

    const defaultButton = buttons.find((button) => button.hasAttribute("data-tab-default")) || buttons[0];
    const defaultTargetId = defaultButton && defaultButton.getAttribute("data-tab-target");
    if (defaultTargetId) activateTab(defaultTargetId);
  });
}

function initSearchInputHandlers() {
  const globalInput = document.getElementById("globalSearchInput");

  if (globalInput) {
    globalInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        runGlobalSearch();
      }
    });
  }
}

function setGlobalSearchStatus(message = "") {
  const statusEl = document.getElementById("globalSearchStatus");
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.classList.toggle("hidden", !message);
}

function runGlobalSearch() {
  const globalInput = document.getElementById("globalSearchInput");
  const query = globalInput?.value?.trim() || "";
  if (!query) {
    if (globalInput) {
      globalInput.focus();
      globalInput.setAttribute("placeholder", t("global_search_empty"));
    }
    setGlobalSearchStatus(t("global_search_empty"));
    return;
  }
  setGlobalSearchStatus(formatMessage(t("global_search_running"), { query }));

  const onHomePage = window.location.pathname === "/";
  if (onHomePage) {
    searchSuppliers("keyword");
    const resultsWrap = document.getElementById("supplierCards");
    if (resultsWrap) {
      resultsWrap.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    return;
  }

  setGlobalSearchStatus(t("global_search_redirect"));
  window.location.href = `/?keyword=${encodeURIComponent(query)}`;
}

function startGlobalVoiceSearch() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    setGlobalSearchStatus(t("home_voice_not_supported"));
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = getLangMode() === "english" ? "en-IN" : "hi-IN";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  setGlobalSearchStatus(t("global_voice_listening"));

  recognition.onresult = (event) => {
    const transcript = event.results?.[0]?.[0]?.transcript?.trim() || "";
    if (!transcript) {
      setGlobalSearchStatus(t("global_voice_error"));
      return;
    }
    const globalInput = document.getElementById("globalSearchInput");
    if (globalInput) globalInput.value = transcript;
    setGlobalSearchStatus(formatMessage(t("global_voice_detected"), { query: transcript }));
    runGlobalSearch();
  };

  recognition.onerror = () => {
    setGlobalSearchStatus(t("global_voice_error"));
  };
  recognition.start();
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

function showToast({ title = "GraminHub", message, variant = "info", timeoutMs = 3500 } = {}) {
  const wrap = document.getElementById("toastWrap");
  if (!wrap || !message) return;
  const toast = document.createElement("div");
  const safeVariant = ["success", "error", "info"].includes(variant) ? variant : "info";
  toast.className = `gh-toast gh-toast-${safeVariant}`;
  toast.innerHTML = `
    <div class="gh-toast-title">${escapeHtml(title)}</div>
    <div class="gh-toast-body">${escapeHtml(message)}</div>
  `;
  wrap.appendChild(toast);
  window.setTimeout(() => toast.remove(), timeoutMs);
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
  const wrapped =
    value && typeof value === "object" && value.status !== undefined && value.data !== undefined;
  const status = wrapped ? Number(value.status) : 200;
  const payload = wrapped ? value.data : value;
  const debugRaw = localStorage.getItem("gh_debug") === "1";

  if (debugRaw) {
    setText(id, JSON.stringify(payload, null, 2));
    return;
  }

  const message = summarizePayload(payload, status);
  setText(id, message);

  if (["loginResult", "profileResult", "actionResult", "supplierResult", "supplierManageOutput", "adminOutput"].includes(id)) {
    showToast({
      title: "GraminHub",
      message: message.split("\n")[0].slice(0, 160),
      variant: status >= 400 ? "error" : "success",
    });
  }
}

function summarizePayload(payload, status = 200) {
  if (payload === null || payload === undefined) {
    return status >= 400 ? "Request failed." : "Done.";
  }

  if (typeof payload === "string") {
    return payload;
  }

  if (Array.isArray(payload)) {
    if (payload.length === 0) return t("home_no_suppliers");
    return `Results: ${payload.length}`;
  }

  if (typeof payload === "object") {
    if (payload.detail) return String(payload.detail);
    if (payload.message) return String(payload.message);
    if (payload.access_token) return "Login successful. Redirecting…";

    const looksLikeUser =
      payload.id !== undefined &&
      payload.name !== undefined &&
      payload.role !== undefined &&
      (payload.email !== undefined || payload.phone !== undefined);
    if (looksLikeUser) {
      const lines = [];
      lines.push(`${t("profile_name_label")}: ${payload.name}`);
      if (payload.email) lines.push(`${t("profile_email_label")}: ${payload.email}`);
      if (payload.phone) lines.push(`${t("profile_phone_label")}: ${payload.phone}`);
      lines.push(`${t("nav_role_prefix")} ${roleLabel(payload.role)}`);
      return lines.join("\n");
    }

    if (payload.booking_id) return `Booking created: #${payload.booking_id}`;
    if (payload.id !== undefined) return `Saved. ID: ${payload.id}`;
  }

  return status >= 400 ? "Request failed." : "Done.";
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
  const path = window.location.pathname;

  // Supplier/Admin use role dashboards as their primary landing view.
  if (path === "/" && (role === "supplier" || role === "admin")) {
    window.location.href = dashboardPathForRole(role);
    return;
  }

  // Only buyer/user should use generic profile panel/page.
  if (["/profile", "/profile/", "/account", "/account/"].includes(path)) {
    if (role === "guest") {
      window.location.href = "/login";
      return;
    }
    if (role === "supplier" || role === "admin") {
      window.location.href = dashboardPathForRole(role);
      return;
    }
  }

  if (!canAccessCurrentPage(role)) {
    window.location.href = "/login";
  }
}

function setNavItemActive(navItem, isActive) {
  if (!navItem || navItem.classList.contains("hidden")) return;

  navItem.classList.toggle("gh-nav-link-active", Boolean(isActive));
  navItem.setAttribute("aria-current", isActive ? "page" : "false");
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
  setNavItemActive(navProfile, isProfilePanelOpen);

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
  const navHome = document.getElementById("navHome");
  const isAuthenticated = role !== "guest";
  const isRoleDashboardOnly = role === "supplier" || role === "admin";

  if (navLogin) {
    navLogin.classList.toggle("hidden", isAuthenticated);
  }
  if (navRegister) {
    navRegister.classList.toggle("hidden", isAuthenticated);
  }
  if (navHome) {
    navHome.classList.toggle("hidden", isRoleDashboardOnly);
  }
  if (navProfile) {
    navProfile.classList.toggle("hidden", !isAuthenticated || isRoleDashboardOnly);
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
  const detail = String(out?.data?.detail || "").toLowerCase();
  const isBlockedAccount = out.status === 403 && detail.includes("blocked");

  if (out.status !== 401 && !isBlockedAccount) {
    return false;
  }
  resetAuthState();
  const messageKey = isBlockedAccount ? "auth_account_blocked" : "auth_session_expired";
  setText(outputId, t(messageKey));
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
  isProfilePanelOpen = false;
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
    if (out.status === 403) {
      setText("actionResult", t("auth_account_blocked"));
    }
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
  const phoneInput = document.getElementById("profilePhone");
  const passwordInput = document.getElementById("profilePassword");

  if (nameInput) nameInput.value = out.data.name || "";
  if (emailInput) emailInput.value = out.data.email || "";
  if (phoneInput) phoneInput.value = out.data.phone || "";
  if (passwordInput) passwordInput.value = "";
}

function openProfilePanel() {
  if (currentUserRole === "guest" || !localStorage.getItem("access_token")) {
    window.location.href = "/login";
    return;
  }
  if (currentUserRole === "supplier" || currentUserRole === "admin") {
    window.location.href = dashboardPathForRole(currentUserRole);
    return;
  }
  const panel = document.getElementById("profilePanel");
  if (!panel) return;
  isProfilePanelOpen = true;
  panel.classList.remove("hidden");
  updateNavActiveState();
  loadMyProfile();
}

function closeProfilePanel() {
  const panel = document.getElementById("profilePanel");
  if (!panel) return;
  isProfilePanelOpen = false;
  panel.classList.add("hidden");
  updateNavActiveState();
}

async function saveMyProfile() {
  const nameInput = document.getElementById("profileName");
  const emailInput = document.getElementById("profileEmail");
  const phoneInput = document.getElementById("profilePhone");
  const passwordInput = document.getElementById("profilePassword");
  if (!nameInput || !emailInput || !passwordInput) return;

  const payload = {};
  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const phone = phoneInput?.value?.trim() || "";
  const password = passwordInput.value;

  if (name) payload.name = name;
  if (email) payload.email = email;
  if (phone) payload.phone = phone;
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
  const phone = document.getElementById("regPhone")?.value?.trim() || "";
  if (!phone) {
    setText("registerResult", t("register_phone_required"));
    return;
  }
  const payload = {
    name: document.getElementById("regName").value,
    email: document.getElementById("regEmail").value,
    phone,
    password: document.getElementById("regPassword").value,
    role: document.getElementById("regRole").value,
  };
  const out = await requestJSON("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setJSON("registerResult", out);
}

function getOtpAuthPayload(includeOtp) {
  const phone = document.getElementById("otpPhone")?.value?.trim() || "";
  const role = document.getElementById("otpRole")?.value || "user";
  const payload = { phone, role };
  if (includeOtp) {
    payload.otp = document.getElementById("otpCode")?.value?.trim() || "";
  }
  return payload;
}

async function requestPhoneOtp() {
  const payload = getOtpAuthPayload(false);
  if (!payload.phone) {
    setText("loginResult", t("otp_phone_required"));
    return;
  }

  const out = await requestJSON("/api/auth/otp/request", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (out.status === 200) {
    const otpHint = document.getElementById("otpHint");
    if (otpHint) {
      otpHint.textContent = formatMessage(t("otp_requested"), { otp: out.data.otp || "--" });
    }
  }
  setJSON("loginResult", out);
}

async function verifyPhoneOtpLogin() {
  const payload = getOtpAuthPayload(true);
  const expectedRole = payload.role;
  if (!payload.phone) {
    setText("loginResult", t("otp_phone_required"));
    return;
  }
  if (!payload.otp) {
    setText("loginResult", t("otp_code_required"));
    return;
  }

  const out = await requestJSON("/api/auth/otp/verify", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (out.data.access_token) {
    localStorage.setItem("access_token", out.data.access_token);
    const currentUser = await refreshCurrentUser();
    if (expectedRole === "admin" && currentUser?.role !== "admin") {
      localStorage.removeItem("access_token");
      await refreshCurrentUser();
      setText("loginResult", t("admin_phone_not_allowed"));
      return;
    }
    setJSON("loginResult", out);
    window.location.href = dashboardPathForRole(currentUser?.role || expectedRole);
    return;
  }
  setJSON("loginResult", out);
}

async function loadCategories() {
  const out = await requestJSON("/api/suppliers/categories");
  if (out.status !== 200 || !Array.isArray(out.data)) {
    return;
  }

  categoryNameById = {};
  categoryList = [];
  out.data.forEach((category) => {
    categoryNameById[category.id] = category.name;
    categoryList.push(category);
  });

  populateCategorySelect("categorySelect", { includeAllOption: true, includeDisabled: true });
  populateCategorySelect("svcCategoryId", { enabledOnly: true, placeholder: "Select category" });
  populateCategorySelect("editSvcCategoryId", { enabledOnly: true, placeholder: "Select category" });
  renderComingSoonCategories();
}

function populateCategorySelect(
  selectId,
  { includeAllOption = false, includeDisabled = false, enabledOnly = false, placeholder = "" } = {},
) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const previousSelection = select.value;

  const options = [];
  if (placeholder) {
    options.push(`<option value="">${escapeHtml(placeholder)}</option>`);
  } else if (includeAllOption) {
    options.push(`<option value="">${escapeHtml(t("category_all"))}</option>`);
  } else {
    options.push(`<option value="">${escapeHtml(t("home_category_label"))}</option>`);
  }

  const enabled = categoryList.filter((category) => Boolean(category?.is_enabled));
  const disabled = categoryList.filter((category) => category?.is_enabled === false);

  enabled.forEach((category) => {
    options.push(`<option value="${category.id}">${escapeHtml(category.name)}</option>`);
  });

  if (!enabledOnly && includeDisabled) {
    disabled.forEach((category) => {
      options.push(
        `<option value="${category.id}" disabled>${escapeHtml(category.name)} (Coming Soon)</option>`,
      );
    });
  }

  select.innerHTML = options.join("");
  if (previousSelection && categoryList.some((category) => String(category.id) === previousSelection)) {
    select.value = previousSelection;
  }
}

function renderComingSoonCategories() {
  const wrap = document.getElementById("comingSoonCategories");
  if (!wrap) return;
  const disabled = categoryList.filter((category) => category?.is_enabled === false);
  if (!disabled.length) {
    wrap.innerHTML = `<div class="rounded-xl border border-dashed border-slate-300 bg-white/80 p-3 text-sm text-slate-600">No upcoming categories.</div>`;
    return;
  }

  wrap.innerHTML = disabled
    .map((category) => {
      const icon = CATEGORY_UI_CONFIG[category.key]?.icon || "fa-regular fa-clock";
      return `
        <article class="gh-coming-soon-card">
          <p class="gh-badge-soon"><i class="fa-regular fa-clock"></i> Coming Soon</p>
          <h3 class="mt-2 font-display text-lg font-bold text-slate-900">
            <i class="${escapeHtml(icon)} mr-2 text-brand-700"></i>${escapeHtml(category.name)}
          </h3>
          <p class="mt-1 text-sm text-slate-600">This category will be available soon. Stay connected with GraminHub.</p>
        </article>
      `;
    })
    .join("");
}

function itemPhotoUrls(service) {
  return [service?.photo_url_1, service?.photo_url_2, service?.photo_url_3]
    .map((value) => String(value || "").trim())
    .filter(Boolean);
}

function scrollPhotoStrip(stripId, direction) {
  const strip = document.getElementById(stripId);
  if (!strip) return;
  const delta = Math.max(strip.clientWidth * 0.9, 180);
  strip.scrollBy({ left: direction * delta, behavior: "smooth" });
}

function normalizedItemName(service) {
  return String(service?.item_name || "").trim();
}

function supplierItemCardMarkup(supplier, service) {
  const photoUrls = itemPhotoUrls(service);
  const stripId = `itemPhotos-${supplier.id}-${service.id}`;
  const photoSlider = photoUrls.length
    ? `<div class="rounded-lg border border-slate-200 bg-white p-2">
        <div class="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">${escapeHtml(
          t("home_item_photos_label"),
        )}</div>
        <div class="flex items-center gap-2">
          <button type="button" class="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-bold text-slate-700 hover:bg-slate-100" onclick="scrollPhotoStrip('${stripId}', -1)">&#8249;</button>
          <div id="${stripId}" class="gh-photo-strip flex flex-1 gap-2 overflow-x-auto">
            ${photoUrls
              .map(
                (url) => `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">
                <img src="${escapeHtml(url)}" alt="Item photo" class="h-24 w-32 min-w-[8rem] rounded-md border border-slate-200 object-cover" loading="lazy" />
              </a>`,
              )
              .join("")}
          </div>
          <button type="button" class="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-bold text-slate-700 hover:bg-slate-100" onclick="scrollPhotoStrip('${stripId}', 1)">&#8250;</button>
        </div>
      </div>`
    : "";

  return `<article class="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
      ${photoSlider}
      <h3 class="mt-3 font-display text-lg font-bold text-slate-900">${escapeHtml(normalizedItemName(service))}</h3>
      ${
        service.item_variant
          ? `<p class="mt-1 text-xs text-slate-700">${escapeHtml(t("home_item_variant_label"))} ${escapeHtml(
              service.item_variant,
            )}</p>`
          : ""
      }
      ${
        service.item_details
          ? `<p class="mt-1 text-xs text-slate-700">${escapeHtml(t("home_item_details_label"))} ${escapeHtml(
              service.item_details,
            )}</p>`
          : ""
      }
      ${
        service.price
          ? `<p class="mt-1 text-xs font-semibold text-emerald-700">${escapeHtml(t("home_item_price_label"))} ${escapeHtml(
              String(service.price),
            )}</p>`
          : ""
      }
      <p class="mt-1 text-xs text-slate-600">${escapeHtml(t("home_item_availability_label"))} ${escapeHtml(
        service.availability || "-",
      )}</p>

      <div class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
        <p class="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">${escapeHtml(
          t("home_supplier_details_label"),
        )}</p>
        <div class="mt-1 flex items-start justify-between gap-2">
          <h4 class="font-semibold text-slate-900">${escapeHtml(supplier.business_name)}</h4>
          <span class="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700">${escapeHtml(
            t("home_supplier_id_prefix"),
          )} ${supplier.id}</span>
        </div>
        <p class="mt-1 text-sm text-slate-600">${escapeHtml(supplier.address)}</p>
        ${
          siteSettings.show_supplier_phone && supplier.phone
            ? `<p class="mt-1 text-sm font-semibold text-slate-800">${escapeHtml(
                t("home_contact_number"),
              )} <span class="text-slate-900">${escapeHtml(supplier.phone)}</span></p>`
            : `<p class="mt-1 text-sm font-semibold text-slate-500">${escapeHtml(t("home_contact_number"))} Hidden</p>`
        }
        <p class="mt-1 text-sm text-amber-700">
          ${escapeHtml(t("home_rating_label"))} ${ratingStars(supplier.average_rating)} (${Number(
            supplier.average_rating || 0,
          ).toFixed(1)}/5, ${supplier.total_reviews || 0} ${escapeHtml(t("home_reviews_suffix"))})
        </p>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        ${
          siteSettings.enable_supplier_call
            ? `<button onclick="callSupplier(${supplier.id})" class="rounded-xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">${escapeHtml(
                t("home_call_btn"),
              )}</button>`
            : ""
        }
        ${
          siteSettings.enable_supplier_whatsapp
            ? `<button onclick="bookViaWhatsApp(${supplier.id})" class="rounded-xl bg-green-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-green-700">${escapeHtml(
                t("home_book_whatsapp_btn"),
              )}</button>`
            : ""
        }
        <button onclick="rateSupplier(${supplier.id})" class="rounded-xl bg-amber-500 px-3 py-2 text-sm font-semibold text-white transition hover:bg-amber-600">${escapeHtml(
          t("home_rate_btn"),
        )}</button>
      </div>
    </article>`;
}

function upsertSupplierCache(suppliers) {
  suppliers.forEach((supplier) => {
    if (supplier && supplier.id !== undefined) {
      supplierCache[supplier.id] = supplier;
    }
  });
}

function renderSuppliers(suppliers, options = {}) {
  const wrap = document.getElementById("supplierCards");
  if (!wrap) return;
  const emptyMessage = options.emptyMessage || t("home_no_suppliers");

  const itemCards = [];
  suppliers.forEach((supplier) => {
    const services = (Array.isArray(supplier.services) ? supplier.services : []).filter((service) =>
      Boolean(normalizedItemName(service)),
    );
    services.forEach((service) => {
      itemCards.push(supplierItemCardMarkup(supplier, service));
    });
  });

  if (!itemCards.length) {
    wrap.innerHTML = `<div class="rounded-2xl border border-slate-200 bg-white p-5 text-slate-600 shadow-sm">${escapeHtml(emptyMessage)}</div>`;
    return;
  }

  wrap.innerHTML = itemCards.join("");
}

function homeCategoryItemCardMarkup(supplier, service) {
  const firstPhoto = itemPhotoUrls(service)[0];
  return `<article class="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      ${
        firstPhoto
          ? `<a href="${escapeHtml(firstPhoto)}" target="_blank" rel="noopener noreferrer">
        <img src="${escapeHtml(firstPhoto)}" alt="Item photo" class="h-28 w-full rounded-lg border border-slate-200 object-cover" loading="lazy" />
      </a>`
          : ""
      }
      <h4 class="mt-2 font-display text-base font-bold text-slate-900">${escapeHtml(normalizedItemName(service))}</h4>
      ${
        service.item_variant
          ? `<p class="mt-1 text-xs text-slate-700">${escapeHtml(t("home_item_variant_label"))} ${escapeHtml(
              service.item_variant,
            )}</p>`
          : ""
      }
      ${
        service.item_details
          ? `<p class="mt-1 text-xs text-slate-600">${escapeHtml(service.item_details)}</p>`
          : ""
      }
      <p class="mt-1 text-xs font-semibold text-slate-800">${escapeHtml(supplier.business_name)}${
        siteSettings.show_supplier_phone && supplier.phone ? ` | ${escapeHtml(supplier.phone)}` : ""
      }</p>
      <div class="mt-2 flex flex-wrap gap-2">
        ${
          siteSettings.enable_supplier_call
            ? `<button onclick="callSupplier(${supplier.id})" class="rounded-lg bg-blue-600 px-2.5 py-1.5 text-xs font-semibold text-white transition hover:bg-blue-700">${escapeHtml(
                t("home_call_btn"),
              )}</button>`
            : ""
        }
        ${
          siteSettings.enable_supplier_whatsapp
            ? `<button onclick="bookViaWhatsApp(${supplier.id})" class="rounded-lg bg-green-600 px-2.5 py-1.5 text-xs font-semibold text-white transition hover:bg-green-700">${escapeHtml(
                t("home_book_whatsapp_btn"),
              )}</button>`
            : ""
        }
        <button onclick="rateSupplier(${supplier.id})" class="rounded-lg bg-amber-500 px-2.5 py-1.5 text-xs font-semibold text-white transition hover:bg-amber-600">${escapeHtml(
          t("home_rate_btn"),
        )}</button>
      </div>
    </article>`;
}

async function loadSiteSettingsPublic() {
  const out = await requestJSON("/api/public/site-settings");
  if (out.status !== 200 || !out.data) return;
  siteSettings = { ...siteSettings, ...out.data };
}

async function loadSiteSettingsForAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const out = await requestJSON("/api/admin/site-settings");
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  if (out.status === 200) {
    const showPhone = document.getElementById("settingShowPhone");
    const enableCall = document.getElementById("settingEnableCall");
    const enableWhatsapp = document.getElementById("settingEnableWhatsapp");
    if (showPhone) showPhone.checked = Boolean(out.data.show_supplier_phone);
    if (enableCall) enableCall.checked = Boolean(out.data.enable_supplier_call);
    if (enableWhatsapp) enableWhatsapp.checked = Boolean(out.data.enable_supplier_whatsapp);
    setText("adminOutput", "Settings loaded.");
  } else {
    setJSON("adminOutput", out);
  }
}

async function saveSiteSettingsForAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const showPhone = document.getElementById("settingShowPhone")?.checked ?? true;
  const enableCall = document.getElementById("settingEnableCall")?.checked ?? true;
  const enableWhatsapp = document.getElementById("settingEnableWhatsapp")?.checked ?? true;
  const payload = {
    show_supplier_phone: showPhone,
    enable_supplier_call: enableCall,
    enable_supplier_whatsapp: enableWhatsapp,
  };
  const out = await requestJSON("/api/admin/site-settings", { method: "PUT", body: JSON.stringify(payload) });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  if (out.status === 200) {
    setText("adminOutput", "Settings saved.");
    await loadSiteSettingsPublic();
  } else {
    setJSON("adminOutput", out);
  }
}

function homeColumnFilterValue(bucketKey) {
  const config = HOME_CATEGORY_COLUMNS[bucketKey];
  if (!config) return "all";
  const select = document.getElementById(config.filterId);
  return select?.value || "all";
}

function homeColumnFilterMatch(item, bucketKey, filterValue) {
  const config = HOME_CATEGORY_COLUMNS[bucketKey];
  if (!config) return true;
  const option = config.filterOptions.find((entry) => entry.value === filterValue) || config.filterOptions[0];
  if (!option || option.value === "all") return true;
  return textContainsAny(item.searchText, option.keywords.map(normalizeText));
}

function populateHomeColumnFilters() {
  Object.entries(HOME_CATEGORY_COLUMNS).forEach(([bucketKey, config]) => {
    const select = document.getElementById(config.filterId);
    if (!select) return;
    const previous = select.value || "all";
    select.innerHTML = config.filterOptions
      .map(
        (option) => `<option value="${escapeHtml(option.value)}">${escapeHtml(t(option.labelKey))}</option>`,
      )
      .join("");
    const hasPrevious = config.filterOptions.some((option) => option.value === previous);
    select.value = hasPrevious ? previous : "all";
  });
}

function renderHomeCategoryColumns() {
  if (!document.getElementById("homeCategoryColumns")) return;
  populateHomeColumnFilters();

  Object.entries(HOME_CATEGORY_COLUMNS).forEach(([bucketKey, config]) => {
    const wrap = document.getElementById(config.containerId);
    if (!wrap) return;

    const filtered = homeCategoryItems
      .filter((item) => item.bucket === bucketKey)
      .filter((item) => homeColumnFilterMatch(item, bucketKey, homeColumnFilterValue(bucketKey)))
      .sort((a, b) => {
        const ratingDiff = Number(b.supplier.average_rating || 0) - Number(a.supplier.average_rating || 0);
        if (ratingDiff !== 0) return ratingDiff;
        return Number(b.service.id || 0) - Number(a.service.id || 0);
      })
      .slice(0, 3);

    if (!filtered.length) {
      wrap.innerHTML = `<div class="rounded-xl border border-dashed border-slate-300 bg-white/80 p-3 text-xs text-slate-600">${escapeHtml(
        t("home_col_empty"),
      )}</div>`;
      return;
    }

    wrap.innerHTML = filtered
      .map((item) => homeCategoryItemCardMarkup(item.supplier, item.service))
      .join("");
  });
}

async function loadHomeCategoryItems() {
  if (!document.getElementById("homeCategoryColumns")) return;
  const out = await requestJSON("/api/suppliers/search");
  if (out.status !== 200 || !Array.isArray(out.data)) {
    Object.values(HOME_CATEGORY_COLUMNS).forEach((config) => {
      const wrap = document.getElementById(config.containerId);
      if (wrap) {
        wrap.innerHTML = `<div class="rounded-xl border border-dashed border-rose-300 bg-white/90 p-3 text-xs text-rose-700">${escapeHtml(
          t("home_col_error"),
        )}</div>`;
      }
    });
    return;
  }

  upsertSupplierCache(out.data);
  homeCategoryItems = [];
  out.data.forEach((supplier) => {
    const services = (Array.isArray(supplier.services) ? supplier.services : []).filter((service) =>
      Boolean(normalizedItemName(service)),
    );
    services.forEach((service) => {
      homeCategoryItems.push({
        bucket: inferHomeBucket(supplier, service),
        supplier,
        service,
        searchText: serviceSearchText(supplier, service),
      });
    });
  });
  renderHomeCategoryColumns();
}

function initHomeCategoryFilters() {
  Object.values(HOME_CATEGORY_COLUMNS).forEach((config) => {
    const select = document.getElementById(config.filterId);
    if (!select) return;
    select.addEventListener("change", () => {
      renderHomeCategoryColumns();
    });
  });
}

function renderHomeSearchPrompt() {
  lastRenderedSearchSuppliers = [];
  renderSuppliers([], { emptyMessage: t("home_search_prompt") });
}

function normalizedInputValue(elementId) {
  return document.getElementById(elementId)?.value?.trim() || "";
}

async function searchSuppliers(searchMode = "advanced", options = {}) {
  const silent = options.silent === true;
  const categoryId = document.getElementById("categorySelect")?.value || "";
  const globalQuery = normalizedInputValue("globalSearchInput");
  const advancedQuery = normalizedInputValue("supplierQuery") || globalQuery;
  const keywordQuery = normalizedInputValue("supplierKeyword") || globalQuery;

  const params = new URLSearchParams();
  if (categoryId) {
    params.set("category_id", categoryId);
  }

  if (searchMode === "keyword") {
    if (!keywordQuery) {
      setText("actionResult", t("home_keyword_required"));
      return;
    }
    if (keywordQuery) {
      params.set("keyword", keywordQuery);
    }
  } else {
    if (advancedQuery) {
      params.set("q", advancedQuery);
    }
    if (keywordQuery) {
      params.set("keyword", keywordQuery);
    }
  }

  const query = params.toString();
  const out = await requestJSON(`/api/suppliers/search${query ? `?${query}` : ""}`);

  if (out.status !== 200 || !Array.isArray(out.data)) {
    lastRenderedSearchSuppliers = [];
    renderSuppliers([], { emptyMessage: t("home_no_suppliers") });
    if (!silent) {
      setJSON("actionResult", out);
    }
    return;
  }

  lastRenderedSearchSuppliers = out.data;
  upsertSupplierCache(out.data);

  renderSuppliers(lastRenderedSearchSuppliers, { emptyMessage: t("home_no_suppliers") });
  if (!silent) {
    setText("actionResult", formatMessage(t("home_search_result_count"), { count: out.data.length }));
  }
}

function applyQuickTag(tagValue) {
  const globalInput = document.getElementById("globalSearchInput");
  if (!globalInput) {
    return;
  }
  globalInput.value = tagValue;
  runGlobalSearch();
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

function normalizeDialPhone(raw) {
  const digits = String(raw || "").replace(/\D/g, "");
  if (!digits) return "";
  if (digits.length === 10) return `+91${digits}`;
  if (digits.length === 11 && digits.startsWith("0")) return `+91${digits.slice(1)}`;
  if (digits.startsWith("91") && digits.length === 12) return `+${digits}`;
  if (digits.startsWith("0") && digits.length > 1) return `+${digits.slice(1)}`;
  return digits.startsWith("+") ? digits : `+${digits}`;
}

function isMobileDevice() {
  return /Android|iPhone|iPad|iPod|Mobi/i.test(navigator.userAgent || "");
}

function triggerPhoneCall(rawPhone) {
  const phone = normalizeDialPhone(rawPhone);
  if (!phone) return false;

  if (!isMobileDevice()) {
    showToast({ title: "Call", message: `Call this number: ${phone}`, variant: "info", timeoutMs: 6000 });
    return false;
  }

  const link = document.createElement("a");
  link.href = `tel:${phone}`;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
  return true;
}

async function callSupplier(supplierId) {
  const supplier = supplierCache[supplierId];
  const token = localStorage.getItem("access_token");

  if (!token) {
    if (supplier && supplier.phone) {
      setText("actionResult", formatMessage(t("action_guest_direct_call"), { phone: supplier.phone }));
      triggerPhoneCall(supplier.phone);
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
    if (out.data?.phone) {
      triggerPhoneCall(out.data.phone);
    }
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
  if (token && !["user", "admin"].includes(currentUserRole)) {
    setText("actionResult", t("buyer_action_only"));
    return;
  }
  // Pre-open the tab to avoid popup blockers (some browsers block window.open after async awaits).
  const pendingTab = window.open("", "_blank");
  let out;

  if (token) {
    const payload = { supplier_id: supplierId, description };
    out = await requestJSON("/api/bookings/whatsapp", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } else {
    const prefilledGuestName = normalizedInputValue("guestNameInput");
    const prefilledGuestPhone = normalizedInputValue("guestPhoneInput");

    const guestName = prefilledGuestName || window.prompt(t("prompt_guest_name"), "");
    if (guestName === null || guestName.trim().length < 2) {
      if (pendingTab) pendingTab.close();
      setText("actionResult", t("error_guest_name"));
      return;
    }

    const guestPhone = prefilledGuestPhone || window.prompt(t("prompt_guest_phone"), "");
    if (guestPhone === null || !isLikelyPhoneNumber(guestPhone)) {
      if (pendingTab) pendingTab.close();
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
    if (pendingTab) pendingTab.close();
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
    if (pendingTab) {
      pendingTab.location.href = out.data.whatsapp_url;
    } else {
      window.open(out.data.whatsapp_url, "_blank");
    }
  } else if (pendingTab) {
    pendingTab.close();
  }
}

async function rateSupplier(supplierId) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    setText("actionResult", t("error_login_for_rating"));
    return;
  }
  if (!["user", "admin"].includes(currentUserRole)) {
    setText("actionResult", t("buyer_action_only"));
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
    business_name: document.getElementById("spBusiness").value.trim(),
    phone: document.getElementById("spPhone").value.trim(),
    address: document.getElementById("spAddress").value.trim(),
  };
  const hasAllRequired = payload.business_name && payload.phone && payload.address;
  if (!hasAllRequired) {
    setText("supplierResult", t("error_supplier_profile_fields_required"));
    return;
  }

  const endpoint = activeSupplierProfileId
    ? `/api/suppliers/profiles/${activeSupplierProfileId}`
    : "/api/suppliers/profile";
  const method = activeSupplierProfileId ? "PUT" : "POST";
  const out = await requestJSON(endpoint, { method, body: JSON.stringify(payload) });
  if (handleUnauthorizedResult(out, "supplierResult")) return;
  if (out.status === 200 && out.data && typeof out.data.id === "number") {
    activeSupplierProfileId = out.data.id;
    setText(
      "supplierResult",
      formatMessage(t("supplier_profile_saved_with_id"), { supplierId: out.data.id }),
    );
    return;
  }
  setJSON("supplierResult", out);
}

async function loadSupplierSetupProfile() {
  if (!document.getElementById("spBusiness")) return;
  if (!["supplier", "admin"].includes(currentUserRole)) return;

  const meOut = await requestJSON("/api/users/me");
  if (meOut.status === 200) {
    const phoneInput = document.getElementById("spPhone");
    if (phoneInput && !phoneInput.value.trim() && meOut.data?.phone) {
      phoneInput.value = meOut.data.phone;
    }
  }

  const out = await requestJSON("/api/suppliers/me/profiles");
  if (out.status !== 200 || !Array.isArray(out.data) || out.data.length === 0) {
    activeSupplierProfileId = null;
    return;
  }

  const latestProfile = out.data[0];
  activeSupplierProfileId = latestProfile.id;
  const businessInput = document.getElementById("spBusiness");
  const phoneInput = document.getElementById("spPhone");
  const addressInput = document.getElementById("spAddress");
  const editIdInput = document.getElementById("editSupplierId");
  const editBusinessInput = document.getElementById("editSpBusiness");
  const editPhoneInput = document.getElementById("editSpPhone");
  const editAddressInput = document.getElementById("editSpAddress");

  if (businessInput) businessInput.value = latestProfile.business_name || "";
  if (phoneInput) phoneInput.value = latestProfile.phone || "";
  if (addressInput) addressInput.value = latestProfile.address || "";
  if (editIdInput) editIdInput.value = String(latestProfile.id || "");
  if (editBusinessInput) editBusinessInput.value = latestProfile.business_name || "";
  if (editPhoneInput) editPhoneInput.value = latestProfile.phone || "";
  if (editAddressInput) editAddressInput.value = latestProfile.address || "";
}

async function addSupplierService() {
  if (!requireAnyRole(["supplier", "admin"], "supplierResult", "supplier_auth_required")) return;
  const itemName = document.getElementById("svcItemName")?.value.trim() || "";
  const itemDetails = document.getElementById("svcItemDetails")?.value.trim() || "";
  const itemVariant = document.getElementById("svcItemVariant")?.value.trim() || "";
  const categoryRaw = document.getElementById("svcCategoryId")?.value.trim() || "";
  const priceRaw = document.getElementById("svcPrice")?.value.trim() || "";
  const availability = document.getElementById("svcAvailability")?.value.trim() || "available";
  const photo1 = document.getElementById("svcPhoto1")?.value.trim() || "";
  const photo2 = document.getElementById("svcPhoto2")?.value.trim() || "";
  const photo3 = document.getElementById("svcPhoto3")?.value.trim() || "";

  if (!itemName) {
    setText("supplierResult", t("error_item_name_or_details_required"));
    return;
  }

  const payload = {
    item_name: itemName,
    item_details: itemDetails || null,
    item_variant: itemVariant || null,
    availability,
    photo_url_1: photo1 || null,
    photo_url_2: photo2 || null,
    photo_url_3: photo3 || null,
  };

  if (categoryRaw) {
    const categoryId = Number(categoryRaw);
    if (!Number.isFinite(categoryId) || categoryId <= 0) {
      setText("supplierResult", t("error_invalid_category_id"));
      return;
    }
    payload.category_id = categoryId;
  }
  if (priceRaw) {
    const price = Number(priceRaw);
    if (!Number.isFinite(price) || price <= 0) {
      setText("supplierResult", t("error_invalid_price"));
      return;
    }
    payload.price = price;
  }

  const out = await requestJSON("/api/suppliers/services", { method: "POST", body: JSON.stringify(payload) });
  if (handleUnauthorizedResult(out, "supplierResult")) return;
  if (out.status === 200 && out.data?.id) {
    setText("supplierResult", `Item saved. Auto-generated Item ID: ${out.data.id}`);
    return;
  }
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
  if (out.status === 200 && Array.isArray(out.data) && out.data.length > 0) {
    activeSupplierProfileId = out.data[0].id;
  }
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
  if (out.status === 200 && out.data && typeof out.data.id === "number") {
    activeSupplierProfileId = out.data.id;
    const setupBusiness = document.getElementById("spBusiness");
    const setupPhone = document.getElementById("spPhone");
    const setupAddress = document.getElementById("spAddress");
    if (setupBusiness) setupBusiness.value = out.data.business_name || "";
    if (setupPhone) setupPhone.value = out.data.phone || "";
    if (setupAddress) setupAddress.value = out.data.address || "";
  }
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
  const itemName = document.getElementById("editSvcItemName")?.value.trim() || "";
  const itemDetails = document.getElementById("editSvcItemDetails")?.value.trim() || "";
  const itemVariant = document.getElementById("editSvcItemVariant")?.value.trim() || "";
  const priceRaw = document.getElementById("editSvcPrice")?.value.trim() || "";
  const availability = document.getElementById("editSvcAvailability")?.value.trim() || "";
  const photo1 = document.getElementById("editSvcPhoto1")?.value.trim() || "";
  const photo2 = document.getElementById("editSvcPhoto2")?.value.trim() || "";
  const photo3 = document.getElementById("editSvcPhoto3")?.value.trim() || "";

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
  if (itemName) payload.item_name = itemName;
  if (itemDetails) payload.item_details = itemDetails;
  if (itemVariant) payload.item_variant = itemVariant;
  if (availability) payload.availability = availability;
  if (photo1) payload.photo_url_1 = photo1;
  if (photo2) payload.photo_url_2 = photo2;
  if (photo3) payload.photo_url_3 = photo3;

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

async function deleteSupplierServiceById() {
  if (!requireAnyRole(["supplier", "admin"], "supplierManageOutput", "supplier_auth_required")) return;
  const serviceId = Number(document.getElementById("editServiceId")?.value);
  if (!serviceId) {
    setText("supplierManageOutput", t("error_service_id_required"));
    return;
  }

  const out = await requestJSON(`/api/suppliers/services/${serviceId}`, { method: "DELETE" });
  if (handleUnauthorizedResult(out, "supplierManageOutput")) return;
  if (out.status === 200) {
    setText("supplierManageOutput", `Item deleted for Item ID: ${serviceId}`);
    return;
  }
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

async function blockUserByAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const userId = Number(document.getElementById("blockUserId").value);
  if (!userId) {
    setText("adminOutput", t("error_user_id_required"));
    return;
  }
  const out = await requestJSON(`/api/admin/users/${userId}/block`, { method: "POST" });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function unblockUserByAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const userId = Number(document.getElementById("blockUserId").value);
  if (!userId) {
    setText("adminOutput", t("error_user_id_required"));
    return;
  }
  const out = await requestJSON(`/api/admin/users/${userId}/unblock`, { method: "POST" });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function loadUsersForAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const out = await requestJSON("/api/admin/users");
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function createManagedUserByAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const name = document.getElementById("managedUserName").value.trim();
  const phone = document.getElementById("managedUserPhone").value.trim();
  const role = document.getElementById("managedUserRole").value;
  if (!name || !phone) {
    setText("adminOutput", "Please enter managed user name and phone.");
    return;
  }

  const out = await requestJSON("/api/admin/users", {
    method: "POST",
    body: JSON.stringify({ name, phone, role }),
  });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function createManagedSupplierByAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const ownerName = document.getElementById("managedSupplierOwnerName").value.trim();
  const ownerPhone = document.getElementById("managedSupplierOwnerPhone").value.trim();
  const businessName = document.getElementById("managedSupplierBusiness").value.trim();
  const supplierPhone = document.getElementById("managedSupplierPhone").value.trim();
  const address = document.getElementById("managedSupplierAddress").value.trim();

  if (!ownerName || !ownerPhone || !businessName || !supplierPhone || !address) {
    setText("adminOutput", "Please fill all supplier creation fields.");
    return;
  }

  const out = await requestJSON("/api/admin/suppliers", {
    method: "POST",
    body: JSON.stringify({
      owner_name: ownerName,
      owner_phone: ownerPhone,
      business_name: businessName,
      supplier_phone: supplierPhone,
      address,
    }),
  });
  if (handleUnauthorizedResult(out, "adminOutput")) return;
  setJSON("adminOutput", out);
}

async function deleteSupplierItemByAdmin() {
  if (!requireRole("admin", "adminOutput", "admin_auth_required")) return;
  const serviceId = Number(document.getElementById("adminDeleteServiceId").value);
  if (!serviceId) {
    setText("adminOutput", t("error_service_id_required"));
    return;
  }
  const out = await requestJSON(`/api/admin/services/${serviceId}`, { method: "DELETE" });
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
  const payload = { name: categoryName, is_enabled: false };
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
  initTabs();
  initLanguageToggle();
  initSearchInputHandlers();
  initHomeCategoryFilters();

  // Default font mode aligns with language toggle.
  const body = document.body;
  if (body) {
    body.classList.add(getLangMode() === "english" ? "gh-font-en" : "gh-font-hi");
  }

  const urlParams = new URLSearchParams(window.location.search);
  const prefillKeyword = (urlParams.get("keyword") || urlParams.get("q") || "").trim();
  const globalInput = document.getElementById("globalSearchInput");
  if (globalInput && prefillKeyword) {
    globalInput.value = prefillKeyword;
  }

  await loadSiteSettingsPublic();
  const currentUser = await refreshCurrentUser();
  enforcePageAccess(currentUser);
  await loadCategories();
  await loadSupplierSetupProfile();
  await loadHomeCategoryItems();

  if (document.getElementById("supplierCards")) {
    if (prefillKeyword) {
      await searchSuppliers("keyword", { silent: true });
      return;
    }
    renderHomeSearchPrompt();
  }
});
