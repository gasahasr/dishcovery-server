import SwiftUI
import FirebaseAuth

struct ContentView: View {
    @State private var restaurantName = ""
    @State private var restaurantAddress = ""
    @State private var restaurantLocation = ""
    @State private var showingRestaurantDetail = false
    @State private var isFormValid = false
    @State private var currentUserId: String = ""
    @StateObject private var firestoreManager = FirestoreManager()
    
    var body: some View {
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
                    currentUserId = "" // Clear the user ID on sign out
                }) {
                    Text("Sign Out")
                        .foregroundColor(.red)
                }
                .padding(.bottom)
                
                // Update test button to use the StateObject
                Button(action: {
                    firestoreManager.testUpsertOperations()
                }) {
                    Text("Test Upsert Operations")
                        .foregroundColor(.blue)
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
            .onAppear {
                // Set the current user ID when the view appears
                if let user = Auth.auth().currentUser {
                    currentUserId = user.uid
                    print("Current user ID set to: \(currentUserId)")
                }
            }
        }
    }
    
    private func validateForm() {
        isFormValid = !restaurantName.isEmpty &&
                     !restaurantAddress.isEmpty &&
                     !restaurantLocation.isEmpty &&
                     restaurantLocation.contains(",") // Ensure location has city and state
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
