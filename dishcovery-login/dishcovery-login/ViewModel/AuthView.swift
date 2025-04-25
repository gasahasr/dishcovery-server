import SwiftUI

struct AuthView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var email = ""
    @State private var password = ""
    @State private var isSignUp = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 25) {
                // Logo or App Name
                Text("Dishcovery")
                    .font(.system(size: 40, weight: .bold))
                    .foregroundColor(.blue)
                    .padding(.top, 50)
                
                // Welcome Text
                Text(isSignUp ? "Create Your Account" : "Welcome Back")
                    .font(.title2)
                    .foregroundColor(.gray)
                
                // Input Fields
                VStack(spacing: 15) {
                    TextField("Email", text: $email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                        .padding(.horizontal)
                        .disabled(authViewModel.isLoading)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .padding(.horizontal)
                        .disabled(authViewModel.isLoading)
                }
                
                // Sign In/Up Button
                Button(action: {
                    if isSignUp {
                        authViewModel.signUp(email: email, password: password)
                    } else {
                        authViewModel.signIn(email: email, password: password)
                    }
                }) {
                    if authViewModel.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text(isSignUp ? "Sign Up" : "Sign In")
                            .foregroundColor(.white)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .cornerRadius(10)
                .disabled(authViewModel.isLoading)
                .padding(.horizontal)
                
                // Toggle between Sign In and Sign Up
                Button(action: {
                    isSignUp.toggle()
                }) {
                    Text(isSignUp ? "Already have an account? Sign In" : "Don't have an account? Sign Up")
                        .foregroundColor(.blue)
                }
                .disabled(authViewModel.isLoading)
                
                Spacer()
            }
            .padding()
            .alert("Error", isPresented: $authViewModel.showError) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(authViewModel.errorMessage)
            }
        }
    }
}
