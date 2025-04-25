import SwiftUI
import FirebaseAuth

struct ContentView: View {
    @State private var restaurantName = ""
    @State private var restaurantAddress = ""
    @State private var restaurantLocation = ""
    @State private var showingRestaurantDetail = false
    @State private var isFormValid = false
    @State private var currentUserId: String = ""
    
    // Keep existing authentication states
    @State private var email = ""
    @State private var password = ""
    @State private var userIsLoggedIn = false
    
    var body: some View {
        if userIsLoggedIn {
            NavigationView {
                VStack {
                    Form {
                        Section(header: Text("Restaurant Information")) {
                            TextField("Restaurant Name", text: $restaurantName)
                                .textContentType(.organizationName)
                                .autocapitalization(.words)
                            
                            TextField("Restaurant Address", text: $restaurantAddress)
                                .textContentType(.fullStreetAddress)
                                .autocapitalization(.words)
                            
                            TextField("Location (City, State)", text: $restaurantLocation)
                                .textContentType(.addressCity)
                                .autocapitalization(.words)
                        }
                    }
                    
                    Button(action: {
                        showingRestaurantDetail = true
                    }) {
                        Text("Search Restaurant")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(isFormValid ? Color.blue : Color.gray)
                            .cornerRadius(10)
                    }
                    .disabled(!isFormValid)
                    .padding()
                    
                    Button(action: {
                        try? Auth.auth().signOut()
                        userIsLoggedIn = false
                        currentUserId = ""
                    }) {
                        Text("Sign Out")
                            .foregroundColor(.red)
                    }
                    .padding(.bottom)
                }
                .navigationTitle("Dishcovery")
                .onChange(of: restaurantName) { _, newValue in
                    validateForm()
                }
                .onChange(of: restaurantAddress) { _, newValue in
                    validateForm()
                }
                .onChange(of: restaurantLocation) { _, newValue in
                    validateForm()
                }
                .sheet(isPresented: $showingRestaurantDetail) {
                    RestaurantDetailView(
                        restaurantName: restaurantName,
                        address: restaurantAddress,
                        location: restaurantLocation,
                        userId: currentUserId
                    )
                }
            }
        } else {
            // Keep existing login view
            NavigationView {
                ZStack {
                    Color.white
                    
                    RoundedRectangle(cornerRadius: 30, style: .continuous)
                        .foregroundStyle(.linearGradient(colors: [.pink, .red], startPoint: .topLeading, endPoint: .bottomTrailing))
                        .frame(width: 1000, height: 400)
                        .rotationEffect(.degrees(135))
                        .offset(y: -350)
                    
                    VStack(spacing: 20) {
                        Text("Welcome")
                            .foregroundColor(.white)
                            .font(.system(size: 40, weight: .bold, design: .rounded))
                            .offset(x: -100, y: -100)
                        
                        TextField("Email", text: $email)
                            .foregroundColor(.white)
                            .textFieldStyle(.plain)
                            .placeholder(when: email.isEmpty) {
                                Text("Email")
                                    .foregroundColor(.white)
                                    .bold()
                            }
                        
                        Rectangle()
                            .frame(width: 350, height: 1)
                            .foregroundColor(.white)
                        
                        SecureField("Password", text: $password)
                            .foregroundColor(.white)
                            .textFieldStyle(.plain)
                            .placeholder(when: password.isEmpty) {
                                Text("Password")
                                    .foregroundColor(.white)
                                    .bold()
                            }
                        
                        Rectangle()
                            .frame(width: 350, height: 1)
                            .foregroundColor(.white)
                        
                        Button {
                            login()
                        } label: {
                            Text("Sign in")
                                .bold()
                                .frame(width: 200, height: 40)
                                .background(
                                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                                        .fill(.linearGradient(colors: [.pink, .red], startPoint: .topLeading, endPoint: .bottomTrailing))
                                )
                                .foregroundColor(.white)
                        }
                        .padding(.top)
                        .offset(y: 100)
                        
                        Button {
                            register()
                        } label: {
                            Text("Don't have an account? Sign up")
                                .bold()
                                .foregroundColor(.white)
                        }
                        .padding(.top)
                        .offset(y: 110)
                    }
                    .frame(width: 350)
                }
                .ignoresSafeArea()
            }
        }
    }
    
    private func validateForm() {
        isFormValid = !restaurantName.isEmpty &&
                     !restaurantAddress.isEmpty &&
                     !restaurantLocation.isEmpty &&
                     restaurantLocation.contains(",") // Ensure location has city and state
    }
    
    // Keep existing authentication methods
    func login() {
        Auth.auth().signIn(withEmail: email, password: password) { result, error in
            if error != nil {
                print(error!.localizedDescription)
            } else {
                if let user = Auth.auth().currentUser {
                    currentUserId = user.uid
                    userIsLoggedIn = true
                }
            }
        }
    }
    
    func register() {
        Auth.auth().createUser(withEmail: email, password: password) { result, error in
            if error != nil {
                print(error!.localizedDescription)
            } else {
                if let user = Auth.auth().currentUser {
                    currentUserId = user.uid
                    userIsLoggedIn = true
                }
            }
        }
    }
}

// Keep existing ViewModifier
struct PlaceholderStyle: ViewModifier {
    var showPlaceHolder: Bool
    var placeholder: AnyView
    
    func body(content: Content) -> some View {
        ZStack(alignment: .leading) {
            if showPlaceHolder {
                placeholder
            }
            content
        }
    }
}

// Keep existing View extension
extension View {
    func placeholder<Content: View>(
        when shouldShow: Bool,
        alignment: Alignment = .leading,
        @ViewBuilder placeholder: () -> Content) -> some View {
            
        modifier(PlaceholderStyle(showPlaceHolder: shouldShow,
                                placeholder: AnyView(placeholder())))
    }
}
