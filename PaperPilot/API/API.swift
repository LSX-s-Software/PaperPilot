//
//  API.swift
//  PaperPilot
//
//  Created by mike on 2023/10/11.
//

import GRPC
import NIOHPACK
import SwiftUI

#if os(macOS)
import AppKit
#else
import UIKit
#endif

final class API {
    static let eventLoopGroup = PlatformSupport.makeEventLoopGroup(loopCount: 1, networkPreference: .best)
    static let builder = ClientConnection.usingPlatformAppropriateTLS(for: eventLoopGroup)
    let channel: ClientConnection = builder.connect(host: "paperpilot.jryang.com")

    /// GRPC Monitor public service client
    public var monitor: Monitor_MonitorPublicServiceAsyncClient
    /// GRPC Auth public service client
    public var auth: Auth_AuthPublicServiceAsyncClient
    /// GRPC User public service client
    public var user: User_UserPublicServiceAsyncClient
    /// GRPC Project public service client
    public var project: Project_ProjectPublicServiceAsyncClient
    /// GRPC Paper public service client
    public var paper: Paper_PaperPublicServiceAsyncClient
    /// GRPC Translation public service client
    public var translation: Translation_TranslationPublicServiceAsyncClient

    static var shared = API()

    @AppStorage(AppStorageKey.User.accessToken.rawValue)
    private var accessToken: String?
    @AppStorage(AppStorageKey.User.accessTokenExpireTime.rawValue)
    private var accessTokenExpireTime: Double?
    @AppStorage(AppStorageKey.User.refreshToken.rawValue)
    private var refreshToken: String?
    @AppStorage(AppStorageKey.User.refreshTokenExpireTime.rawValue)
    private var refreshTokenExpireTime: Double?

    @AppStorage(AppStorageKey.User.id.rawValue)
    private var id: String?
    @AppStorage(AppStorageKey.User.phone.rawValue)
    var phone: String?
    @AppStorage(AppStorageKey.User.avatar.rawValue)
    private var avatar: String?
    @AppStorage(AppStorageKey.User.username.rawValue)
    var username: String?

    init() {
        let factory = ErrorInterceptorFactory()
        self.auth = Auth_AuthPublicServiceAsyncClient(channel: channel, interceptors: factory)
        self.user = User_UserPublicServiceAsyncClient(channel: channel, interceptors: factory)
        self.project = Project_ProjectPublicServiceAsyncClient(channel: channel, interceptors: factory)
        self.paper = Paper_PaperPublicServiceAsyncClient(channel: channel, interceptors: factory)
        self.translation = Translation_TranslationPublicServiceAsyncClient(channel: channel, interceptors: factory)
        self.monitor = Monitor_MonitorPublicServiceAsyncClient(channel: channel, interceptors: factory)

#if os(macOS)
        let notification = NSApplication.willTerminateNotification
#else
        let notification = UIApplication.willTerminateNotification
#endif
        NotificationCenter.default.addObserver(forName: notification, object: nil, queue: .main ) { _ in
            do {
                try self.channel.close().wait()
            } catch {
                print(error.localizedDescription)
            }
        }
    }

    func setToken() {
        guard let accessToken = self.accessToken else {
            return
        }
        let headers: HPACKHeaders = ["authorization": "Bearer \(accessToken)"]
        auth.defaultCallOptions.customMetadata = headers
        user.defaultCallOptions.customMetadata = headers
        project.defaultCallOptions.customMetadata = headers
        paper.defaultCallOptions.customMetadata = headers
        translation.defaultCallOptions.customMetadata = headers
    }

    func refreshUserInfo() async throws {
        let result = try await Self.shared.user.getCurrentUser(.init())
        id = result.id
        username = result.username
        phone = result.phone
        avatar = result.avatar
    }

    fileprivate func refreshAccessToken(alert: Alert) async {
        do {
            let result = try await Self.shared.auth.refresh(.with {
                $0.refresh = self.refreshToken!
            })
            self.accessToken = result.access.value
            self.accessTokenExpireTime = Double(result.access.expireTime.seconds)
            print("Refreshed access token.")
            if self.accessTokenExpireTime! > self.refreshTokenExpireTime! {
                print("Refresh token is about to expire.")
                // TODO: Ask for password
            }
            self.scheduleRefreshToken(alert: alert)
        } catch let error as GRPCStatus {
            DispatchQueue.main.async {
                alert.alert(
                    message: String(localized: "Failed to refresh the access token."),
                    detail: error.message ?? "")
            }
        } catch {
            print("Failed to refresh: \(error.localizedDescription)")
        }
    }

    func scheduleRefreshToken(alert: Alert) {
        guard let accessToken = self.accessToken else {
            return
        }
        let accessExpireDate = Date(timeIntervalSince1970: accessTokenExpireTime!)
        let refreshExpireDate = Date(timeIntervalSince1970: refreshTokenExpireTime!)
        let secBeforeExpire: Double = 60.0
        if Date().advanced(by: secBeforeExpire) >= accessExpireDate {
            Task {
                await self.refreshAccessToken(alert: alert)
            }
            return
        }

        let timer = Timer(
            fire: refreshExpireDate.advanced(by: -secBeforeExpire),
            interval: 0,
            repeats: false) { _ in
            Task {
                await self.refreshAccessToken(alert: alert)
            }
        }
        RunLoop.main.add(timer, forMode: .common)
    }
}
